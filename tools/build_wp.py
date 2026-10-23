# WordPress plugin "PiMagic Studio Site": the sandbox design, served by WordPress on the real pages (Christian, 21 Oct 2026 - Craig's
# WordPress version lost the design; "prepare a WordPress for you to insert"). The plugin replaces the theme's output on the front page,
# Tutorials (/about/ or /tutorials/, built live from the WordPress posts), Testimonials, Shop and Contact, plus two new pages /details/ and /gallery/; everything else (EDD checkout, downloads, posts, wp-admin) stays.
# Preview first: logged-in editors see the new design, visitors keep the old pages until Settings > PiMagic Site > "Live" is ticked.
#   python3 tools/build_wp.py   ->  wp/pimagic-site/ and exports/pimagic-site-<version>.zip
import os, re, shutil, subprocess, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import build_pages
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(HERE, "site"); OUT = os.path.join(HERE, "wp", "pimagic-site")
VERSION = "1.2.0"
PAGES = {"home": "index.html", "details": "details/index.html", "gallery": "gallery/index.html", "tutorials": "tutorials/index.html", "testimonials": "testimonials/index.html", "shop": "shop/index.html", "contact": "contact/index.html"}
LINKS = {"details": "details/", "gallery": "gallery/", "shop": "shop/", "tutorials": "about/", "testimonials": "testimonials/", "contact": "contact/"}

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
 * Description: The 2026 PiMagic Studio design (dark, interactive) on the home, details, gallery, tutorials, testimonials, shop and contact pages. Tutorials are built from your posts. Preview mode first: editors see it, visitors keep the old pages until you tick "Live" under Settings &rarr; PiMagic Site.
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
	$v = get_query_var('pms_page');
	if ($v === 'details' || $v === 'gallery') $p = $v;
	elseif (is_front_page()) $p = 'home';
	elseif (is_page('details')) $p = 'details';
	elseif (is_page('gallery')) $p = 'gallery';
	elseif (is_page(array('about', 'tutorials'))) $p = 'tutorials';
	elseif (is_page('testimonials')) $p = 'testimonials';
	elseif (is_page('shop')) $p = 'shop';
	elseif (is_page('contact')) $p = 'contact';
	return $p;
}

add_filter('template_include', function ($t) { return pms_page() ? PMS_DIR . 'render.php' : $t; }, 99);

// /details/ and /gallery/ need no WordPress page: two rewrite rules (also ?pms_page=details with plain permalinks)
add_action('init', function () {
	add_rewrite_rule('^(details|gallery)/?$', 'index.php?pms_page=$matches[1]', 'top');
	if (get_option('pms_rw') !== PMS_VERSION) { flush_rewrite_rules(false); update_option('pms_rw', PMS_VERSION); }
});
add_filter('query_vars', function ($v) { $v[] = 'pms_page'; return $v; });
add_filter('redirect_canonical', function ($r) { return get_query_var('pms_page') ? false : $r; });
add_action('template_redirect', function () {                                 // not live and not an editor: these two do not exist yet
	if (get_query_var('pms_page') && !pms_page()) { global $wp_query; $wp_query->set_404(); status_header(404); nocache_headers(); }
}, 0);
register_deactivation_hook(__FILE__, function () { delete_option('pms_rw'); flush_rewrite_rules(false); });

/** Tutorials from the posts: known posts keep their topic, new ones go under their category; PiMagic 3.2 from the date set in Settings */
function pms_youtube_id($html) {
	return preg_match('~(?:youtube(?:-nocookie)?\.com/(?:watch\?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})~', $html, $m) ? $m[1] : '';
}
function pms_tutorials() {
	$map = json_decode(file_get_contents(PMS_DIR . 'pages/tutorials.json'), true);
	$posts = get_posts(array('post_type' => 'post', 'post_status' => 'publish', 'numberposts' => -1, 'orderby' => 'date', 'order' => 'DESC'));
	if (!$posts) return null;
	$v3 = strtotime(get_option('pms_v3_date', '2026-10-15') . ' 00:00:00');
	$fresh = array(); $known = array(); $order = array();
	foreach ($map['topics'] as $t) { $order[$t[0]] = array($t[1], $t[2]); $known[$t[0]] = array(); }
	foreach ($posts as $post) {
		$slug = $post->post_name; $k = isset($map['posts'][$slug]) ? $map['posts'][$slug]['t'] : '';
		if (!$k) {
			$k = 'more'; $name = 'More tutorials'; $sub = '';
			foreach (get_the_category($post->ID) as $c) if ($c->slug !== 'uncategorized') { $k = 'c-' . $c->slug; $name = $c->name; $sub = wp_strip_all_tags(category_description($c->term_id)); break; }
			if (!isset($fresh[$k])) $fresh[$k] = array($name, $sub, array());
		}
		$yt = pms_youtube_id($post->post_content);
		$v = strtotime($post->post_date) >= $v3 ? '3.2' : '2';
		$title = isset($map['posts'][$slug]) ? $map['posts'][$slug]['title'] : get_the_title($post);
		$desc = isset($map['posts'][$slug]) ? $map['posts'][$slug]['desc'] : wp_trim_words(wp_strip_all_tags(has_excerpt($post) ? $post->post_excerpt : strip_shortcodes($post->post_content)), 22);
		$thumb = $yt ? 'https://i.ytimg.com/vi/' . $yt . '/hqdefault.jpg' : (string) get_the_post_thumbnail_url($post, 'medium_large');
		$img = $thumb ? '<img src="' . esc_url($thumb) . '" alt="" loading="lazy">' : '';
		$head = $yt ? '<button class="tut-thumb" data-yt="' . esc_attr($yt) . '" aria-label="Play: ' . esc_attr($title) . '">' . $img . '<span class="tut-play"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span></button>'
		            : '<a class="tut-thumb" href="' . esc_url(get_permalink($post)) . '">' . $img . '</a>';
		$card = '<article class="tut glass" data-topic="' . esc_attr($k) . '" data-v="' . $v . '">' . $head . '<div class="tut-body"><p class="tut-meta mono"><span class="badge">PiMagic ' . $v . '</span>'
		      . esc_html(date_i18n('M Y', strtotime($post->post_date))) . '</p><h3>' . esc_html($title) . '</h3><p>' . esc_html($desc) . '</p><a class="tut-link" href="' . esc_url(get_permalink($post)) . '">Read the post &rarr;</a></div></article>';
		if (isset($fresh[$k])) $fresh[$k][2][] = $card;
		else $known[$k][(int) $map['posts'][$slug]['i']] = $card;
	}
	$secs = array();                                                             // new categories first, then the known topics
	foreach ($fresh as $k => $f) if ($k !== 'more') $secs[] = array($k, $f[0], $f[1], $f[2]);
	foreach ($order as $k => $f) if ($known[$k]) { ksort($known[$k]); $secs[] = array($k, $f[0], $f[1], $known[$k]); }
	if (isset($fresh['more'])) $secs[] = array('more', $fresh['more'][0], $fresh['more'][1], $fresh['more'][2]);   // posts without a category last
	$chips = '<button class="on" data-t="all">All topics</button>'; $html = '';
	foreach ($secs as $x) {
		$chips .= '<button data-t="' . esc_attr($x[0]) . '">' . esc_html($x[1]) . '</button>';
		$html .= '<section class="topic" id="t-' . esc_attr($x[0]) . '"><div class="topic-head"><h2>' . esc_html($x[1]) . '</h2><p>' . esc_html($x[2]) . '</p></div><div class="tut-grid">' . implode('', $x[3]) . '</div></section>' . "\n";
	}
	return array($chips, $html);
}

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
	register_setting('pms', 'pms_v3_date', array('type' => 'string', 'default' => '2026-10-15', 'sanitize_callback' => function ($v) { return preg_match('/^\d{4}-\d{2}-\d{2}$/', $v) ? $v : '2026-10-15'; }));
});
function pms_settings_page() {
	$live = get_option('pms_live') === '1'; $form = (int) get_option('pms_form_id', 63); $v3 = get_option('pms_v3_date', '2026-10-15');
	echo '<div class="wrap"><h1>PiMagic Studio Site</h1>';
	echo '<p>The new design replaces the theme on the <b>front page</b>, <b>Tutorials</b> (page slug <code>about</code> or <code>tutorials</code>), <b>Testimonials</b>, <b>Shop</b> and <b>Contact</b>, and adds two pages of its own: <a href="' . esc_url(home_url('/details/')) . '">/details/</a> and <a href="' . esc_url(home_url('/gallery/')) . '">/gallery/</a>. The Tutorials page lists your posts by itself: publish a post with a YouTube video and it appears there. Shop checkout, downloads, tutorial posts and all other pages are untouched.</p>';
	echo '<p>Status: ' . ($live ? '<b style="color:#1a7f37">LIVE</b> &mdash; every visitor sees the new design.' : '<b style="color:#9a6700">PREVIEW</b> &mdash; only logged-in editors see the new design; visitors see the old pages.') . ' Editors can add <code>?pimagic=0</code> to any of these pages to see the old version.</p>';
	echo '<form method="post" action="options.php">'; settings_fields('pms');
	echo '<table class="form-table"><tr><th>Live for all visitors</th><td><label><input type="checkbox" name="pms_live" value="1" ' . checked($live, true, false) . '> Show the new design to everyone</label></td></tr>';
	echo '<tr><th>Contact form</th><td><input type="number" name="pms_form_id" value="' . esc_attr($form) . '" class="small-text"> WPForms form ID shown on the Contact page</td></tr>';
	echo '<tr><th>PiMagic 3.2 tutorials from</th><td><input type="date" name="pms_v3_date" value="' . esc_attr($v3) . '"> Posts from this date on are marked &ldquo;PiMagic 3.2&rdquo;; older ones are the PiMagic 2 archive</td></tr></table>';
	submit_button(); echo '</form></div>';
}
add_action('admin_notices', function () {
	if (get_option('pms_live') === '1' || !current_user_can('manage_options')) return;
	$s = get_current_screen(); if ($s && $s->id === 'settings_page_pimagic-site') return;
	echo '<div class="notice notice-info"><p><b>PiMagic Studio Site</b> is in preview: you see the new design on the home, details, gallery, tutorials, testimonials, shop and contact pages; visitors do not yet. <a href="' . esc_url(home_url('/')) . '">Look at it</a> &middot; <a href="' . esc_url(admin_url('options-general.php?page=pimagic-site')) . '">Go live</a></p></div>';
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
if ($page === 'tutorials' && ($t = pms_tutorials())) {
	$html = preg_replace('~<!--PMS:CHIPS-->.*?<!--/PMS:CHIPS-->~s', $t[0], $html, 1);
	$html = preg_replace_callback('~<!--PMS:TUT-->.*?<!--/PMS:TUT-->~s', function () use ($t) { return $t[1]; }, $html, 1);
}
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
2. Nothing changes for visitors yet. While you are logged in, open the home page, /details/, /gallery/, Tutorials, Testimonials, Shop and Contact:
   you see the new design. Add ?pimagic=0 to a page address to compare with the old one.
3. Happy? Settings > PiMagic Site > tick "Live for all visitors" > Save. To go back, untick it (or deactivate the plugin).

WHAT IT DOES
- Replaces the theme's output on: the front page, the Tutorials page (slug about or tutorials), Testimonials, Shop, Contact.
- Adds two pages: /details/ (everything inside PiMagic Studio) and /gallery/. No WordPress pages needed for them.
- Tutorials: built from your posts every time. Publish a post with a YouTube video and it appears; its category becomes its topic.
  Posts from the date in Settings > PiMagic Site on are marked PiMagic 3.2, older ones are the PiMagic 2 archive.
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
json.dump({"topics": build_pages.TOPICS, "posts": {x[4]: {"t": x[0], "title": x[1], "desc": x[5], "i": i} for i, x in enumerate(build_pages.T)}},
          open(os.path.join(OUT, "pages", "tutorials.json"), "w"), ensure_ascii=False)
open(os.path.join(OUT, "pimagic-site.php"), "w").write(PHP.replace("%VERSION%", VERSION))
open(os.path.join(OUT, "render.php"), "w").write(RENDER)
open(os.path.join(OUT, "readme.txt"), "w").write(README.replace("%VERSION%", VERSION))
open(os.path.join(OUT, "index.php"), "w").write("<?php // Silence is golden.\n")
z = os.path.join(HERE, "exports", f"pimagic-site-{VERSION}.zip"); os.makedirs(os.path.dirname(z), exist_ok=True)
if os.path.exists(z): os.remove(z)
subprocess.run(["zip", "-qr", "-X", z, "pimagic-site", "-x", "*.DS_Store", "*/._*"], cwd=os.path.dirname(OUT), check=True)
left = subprocess.run(["grep", "-rn", "-E", 'href="\\.\\./|="assets/|="css/|="js/', os.path.join(OUT, "pages")], capture_output=True, text=True).stdout
print("plugin ok:", z, os.path.getsize(z) // 1024 // 1024, "MB", "| unconverted paths:", left.count("\n"))
