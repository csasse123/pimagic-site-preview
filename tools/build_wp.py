# WordPress plugin "PiMagic Studio Site": the sandbox design, served by WordPress on the real pages (Christian, 21 Oct 2026 - Craig's
# WordPress version lost the design; "prepare a WordPress for you to insert"). The plugin replaces the theme's output on the front page,
# Tutorials (/about/ or /tutorials/), Testimonials, Shop and Contact; everything else (EDD checkout, downloads, posts, wp-admin) stays.
# Preview first: logged-in editors see the new design, visitors keep the old pages until Settings > PiMagic Site > "Live" is ticked.
#   python3 tools/build_wp.py   ->  wp/pimagic-site/ and exports/pimagic-site-<version>.zip
import os, re, shutil, subprocess
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(HERE, "site"); OUT = os.path.join(HERE, "wp", "pimagic-site")
VERSION = "1.0.0"
PAGES = {"home": "index.html", "tutorials": "tutorials/index.html", "testimonials": "testimonials/index.html", "shop": "shop/index.html", "contact": "contact/index.html"}
LINKS = {"shop": "shop/", "tutorials": "about/", "testimonials": "testimonials/", "contact": "contact/"}

def to_template(html, page):
    h = html
    h = re.sub(r'\s*<meta name="robots" content="noindex, nofollow"><!-- sandbox: remove at launch -->', "", h)
    h = re.sub(r'<html lang="en"( data-base="\.\./")?>', '<html lang="en" data-base="{{BASE}}">', h)
    h = h.replace("<title>", "<title>").replace("</head>", "{{WP_HEAD}}\n</head>").replace("</body>", "{{WP_FOOTER}}\n</body>")
    for pre in ('="../', '="'):                                  # site assets
        for d in ("assets/", "css/", "js/"): h = h.replace(pre + d, '="{{BASE}}' + d)
    h = h.replace("url(../assets/", "url({{BASE}}assets/")
    for k, v in LINKS.items():                                   # the sandbox's own pages -> the WordPress pages
        h = h.replace(f'href="../{k}/', f'href="{{{{HOME}}}}{v}').replace(f'href="{k}/', f'href="{{{{HOME}}}}{v}')
    h = h.replace('href="../#', 'href="{{HOME}}#').replace('href="../"', 'href="{{HOME}}"')
    h = h.replace("https://pimagicstudio.com/", "{{HOME}}")       # live links work on any domain (staging too)
    if page == "contact":                                        # the real WPForms form inside the design
        h = re.sub(r'<form class="cform glass reveal" id="cform".*?</form>', '<div class="cform cform-wp glass reveal">{{CONTACT_FORM}}</div>', h, flags=re.S)
    assert "{{WP_HEAD}}" in h and "{{WP_FOOTER}}" in h and "{{BASE}}" in h
    return h

PHP = r'''<?php
/**
 * Plugin Name: PiMagic Studio Site
 * Description: The 2026 PiMagic Studio design (dark, interactive) on the home, tutorials, testimonials, shop and contact pages. Preview mode first: editors see it, visitors keep the old pages until you tick "Live" under Settings &rarr; PiMagic Site.
 * Version: %VERSION%
 * Author: Dr. Christian Sasse and Craig Stocks
 * Requires at least: 6.0
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) exit;
define('PMS_DIR', plugin_dir_path(__FILE__));
define('PMS_URL', plugin_dir_url(__FILE__));
define('PMS_VERSION', '%VERSION%');

/** which of our pages this request is, or null */
function pms_page() {
	static $p = false;
	if ($p !== false) return $p;
	$p = null;
	if (is_admin() || wp_doing_ajax() || is_feed()) return $p;
	$live = get_option('pms_live') === '1';
	$preview = is_user_logged_in() && current_user_can('edit_pages');
	if (isset($_GET['pimagic']) && $_GET['pimagic'] === '0') return $p;          // editors: compare with the old page
	if (!$live && !$preview) return $p;
	if (is_front_page()) $p = 'home';
	elseif (is_page(array('about', 'tutorials'))) $p = 'tutorials';
	elseif (is_page('testimonials')) $p = 'testimonials';
	elseif (is_page('shop')) $p = 'shop';
	elseif (is_page('contact')) $p = 'contact';
	return $p;
}

add_filter('template_include', function ($t) { return pms_page() ? PMS_DIR . 'render.php' : $t; }, 99);

// on our pages: no theme styles (they would paint the page white); plugins' styles (WPForms, EDD, Jetpack) stay
add_action('template_redirect', function () {
	if (!pms_page()) return;
	remove_action('wp_head', '_wp_render_title_tag', 1);                      // our pages carry their own <title>
	remove_action('wp_enqueue_scripts', 'wp_enqueue_global_styles');
	remove_action('wp_footer', 'wp_enqueue_global_styles', 1);
	remove_action('wp_enqueue_scripts', 'wp_enqueue_classic_theme_styles');
	add_filter('should_load_separate_core_block_assets', '__return_true');
});
add_action('wp_enqueue_scripts', function () {
	if (!pms_page()) return;
	global $wp_styles;
	foreach ((array) $wp_styles->queue as $h) {
		$src = isset($wp_styles->registered[$h]) ? (string) $wp_styles->registered[$h]->src : '';
		if (strpos($src, '/themes/') !== false || in_array($h, array('global-styles', 'wp-block-library', 'wp-block-library-theme', 'classic-theme-styles', 'core-block-supports'), true))
			wp_dequeue_style($h);
	}
}, 100);

// settings: Live switch + the contact form's WPForms id
add_action('admin_menu', function () {
	add_options_page('PiMagic Site', 'PiMagic Site', 'manage_options', 'pimagic-site', 'pms_settings_page');
});
add_action('admin_init', function () {
	register_setting('pms', 'pms_live', array('type' => 'string', 'default' => '0', 'sanitize_callback' => function ($v) { return $v === '1' ? '1' : '0'; }));
	register_setting('pms', 'pms_form_id', array('type' => 'integer', 'default' => 63, 'sanitize_callback' => 'absint'));
});
function pms_settings_page() {
	$live = get_option('pms_live') === '1'; $form = (int) get_option('pms_form_id', 63);
	echo '<div class="wrap"><h1>PiMagic Studio Site</h1>';
	echo '<p>The new design replaces the theme on the <b>front page</b>, <b>Tutorials</b> (page slug <code>about</code> or <code>tutorials</code>), <b>Testimonials</b>, <b>Shop</b> and <b>Contact</b>. Shop checkout, downloads, tutorial posts and all other pages are untouched.</p>';
	echo '<p>Status: ' . ($live ? '<b style="color:#1a7f37">LIVE</b> &mdash; every visitor sees the new design.' : '<b style="color:#9a6700">PREVIEW</b> &mdash; only logged-in editors see the new design; visitors see the old pages.') . ' Editors can add <code>?pimagic=0</code> to any of these pages to see the old version.</p>';
	echo '<form method="post" action="options.php">'; settings_fields('pms');
	echo '<table class="form-table"><tr><th>Live for all visitors</th><td><label><input type="checkbox" name="pms_live" value="1" ' . checked($live, true, false) . '> Show the new design to everyone</label></td></tr>';
	echo '<tr><th>Contact form</th><td><input type="number" name="pms_form_id" value="' . esc_attr($form) . '" class="small-text"> WPForms form ID shown on the Contact page</td></tr></table>';
	submit_button(); echo '</form></div>';
}
add_action('admin_notices', function () {
	if (get_option('pms_live') === '1' || !current_user_can('manage_options')) return;
	$s = get_current_screen(); if ($s && $s->id === 'settings_page_pimagic-site') return;
	echo '<div class="notice notice-info"><p><b>PiMagic Studio Site</b> is in preview: you see the new design on the home, tutorials, testimonials, shop and contact pages; visitors do not yet. <a href="' . esc_url(home_url('/')) . '">Look at it</a> &middot; <a href="' . esc_url(admin_url('options-general.php?page=pimagic-site')) . '">Go live</a></p></div>';
});
add_filter('plugin_action_links_' . plugin_basename(__FILE__), function ($l) {
	array_unshift($l, '<a href="' . esc_url(admin_url('options-general.php?page=pimagic-site')) . '">Settings</a>'); return $l;
});
'''

RENDER = r'''<?php
// Prints one of our pages with the theme's header and footer left out; wp_head()/wp_footer() keep plugins (WPForms, EDD, Jetpack) working.
if (!defined('ABSPATH')) exit;
$page = pms_page();
$html = file_get_contents(PMS_DIR . 'pages/' . $page . '.html');
$form = '';
if ($page === 'contact') $form = do_shortcode('[wpforms id="' . (int) get_option('pms_form_id', 63) . '" title="false" description="false"]');   // before wp_head: its styles load in the head
ob_start(); wp_head(); $head = ob_get_clean();
if (is_admin_bar_showing()) $head .= '<style>.pm-nav{top:32px!important}@media (max-width:782px){.pm-nav{top:46px!important}}</style>';
ob_start(); wp_footer(); $foot = ob_get_clean();
echo str_replace(
	array('{{BASE}}', '{{HOME}}', '{{WP_HEAD}}', '{{WP_FOOTER}}', '{{CONTACT_FORM}}'),
	array(esc_url(PMS_URL . 'site/'), esc_url(home_url('/')), $head, $foot, $form),
	$html
);
'''

README = """=== PiMagic Studio Site ===
Version: %VERSION%

The 2026 PiMagic Studio design on the WordPress site.

INSTALL (about 2 minutes)
1. WordPress admin > Plugins > Add New > Upload Plugin > choose pimagic-site-%VERSION%.zip > Install Now > Activate.
2. Nothing changes for visitors yet. While you are logged in, open the home page, Tutorials, Testimonials, Shop and Contact:
   you see the new design. Add ?pimagic=0 to a page address to compare with the old one.
3. Happy? Settings > PiMagic Site > tick "Live for all visitors" > Save. To go back, untick it (or deactivate the plugin).

WHAT IT DOES
- Replaces the theme's output on: the front page, the Tutorials page (slug about or tutorials), Testimonials, Shop, Contact.
- Everything else is untouched: shop checkout, product downloads, order history, tutorial posts, every other page, wp-admin.
- The Contact page shows your WPForms form (ID 63; change it in Settings > PiMagic Site).
- Buy buttons go to the PiMagic Studio Version 3 product page. Films, images and scripts are inside the plugin.

UPDATES
Install a newer zip the same way: WordPress offers "Replace current with uploaded".
"""

if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "pages"))
for page, src in PAGES.items():
    open(os.path.join(OUT, "pages", page + ".html"), "w").write(to_template(open(os.path.join(SITE, src)).read(), page))
shutil.copytree(os.path.join(SITE, "css"), os.path.join(OUT, "site", "css"))
shutil.copytree(os.path.join(SITE, "js"), os.path.join(OUT, "site", "js"))
shutil.copytree(os.path.join(SITE, "assets"), os.path.join(OUT, "site", "assets"), ignore=shutil.ignore_patterns("meta.json", ".DS_Store", "._*"))
open(os.path.join(OUT, "pimagic-site.php"), "w").write(PHP.replace("%VERSION%", VERSION))
open(os.path.join(OUT, "render.php"), "w").write(RENDER)
open(os.path.join(OUT, "readme.txt"), "w").write(README.replace("%VERSION%", VERSION))
open(os.path.join(OUT, "index.php"), "w").write("<?php // Silence is golden.\n")
z = os.path.join(HERE, "exports", f"pimagic-site-{VERSION}.zip"); os.makedirs(os.path.dirname(z), exist_ok=True)
if os.path.exists(z): os.remove(z)
subprocess.run(["zip", "-qr", "-X", z, "pimagic-site", "-x", "*.DS_Store", "*/._*"], cwd=os.path.dirname(OUT), check=True)
left = subprocess.run(["grep", "-rn", "-E", 'href="\\.\\./|="assets/|="css/|="js/', os.path.join(OUT, "pages")], capture_output=True, text=True).stdout
print("plugin ok:", z, os.path.getsize(z) // 1024 // 1024, "MB", "| unconverted paths:", left.count("\n"))
