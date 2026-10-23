<?php
// TEST ONLY (local WordPress Playground): make a WPForms contact form once and point the PiMagic plugin at it.
add_action('wp_loaded', function () {
	if (get_option('pms_test_form_done') || !function_exists('wpforms') || !post_type_exists('wpforms')) return;
	$fields = array(
		'0' => array('id' => '0', 'type' => 'name', 'label' => 'Name', 'format' => 'first-last', 'required' => '1', 'size' => 'medium'),
		'1' => array('id' => '1', 'type' => 'email', 'label' => 'Email', 'required' => '1', 'size' => 'medium'),
		'2' => array('id' => '2', 'type' => 'textarea', 'label' => 'Comment or Message', 'required' => '1', 'size' => 'medium'),
	);
	$id = wp_insert_post(array('post_type' => 'wpforms', 'post_status' => 'publish', 'post_title' => 'Contact'));
	$data = array('id' => (string) $id, 'field_id' => 3, 'fields' => $fields, 'settings' => array('form_title' => 'Contact', 'submit_text' => 'Submit', 'submit_text_processing' => 'Sending...'));
	wp_update_post(array('ID' => $id, 'post_content' => wp_slash(wp_json_encode($data))));
	update_option('pms_form_id', $id); update_option('pms_test_form_done', 1);
});
// TEST ONLY: a few posts for the Tutorials page - one known (topic from the plugin's list), one new in a category, one with no category
add_action('wp_loaded', function () {
	if (get_option('pms_test_posts_done')) return;
	wp_insert_post(array('post_type' => 'post', 'post_status' => 'publish', 'post_name' => 'smart-mode', 'post_title' => 'Smart Mode', 'post_date' => '2026-04-06 10:00:00',
		'post_content' => '<p>Smart mode video.</p><p>https://www.youtube.com/watch?v=FV1ZQ3JVFYs</p>'));
	$cat = wp_insert_term('PiMagic 3.2 Basics', 'category', array('description' => 'Your first runs with PiMagic Studio 3.2.'));
	wp_insert_post(array('post_type' => 'post', 'post_status' => 'publish', 'post_name' => 'first-run-32', 'post_title' => 'Your first run with 3.2', 'post_date' => '2026-10-20 10:00:00',
		'post_category' => array(is_wp_error($cat) ? 1 : $cat['term_id']), 'post_content' => '<p>Select a folder, press Start: a complete first run with PiMagic Studio 3.2, from raw frames to finished images.</p><!-- wp:embed {"url":"https://youtu.be/oV9ObVXRDPY"} --><figure><div>https://youtu.be/oV9ObVXRDPY</div></figure><!-- /wp:embed -->'));
	wp_insert_post(array('post_type' => 'post', 'post_status' => 'publish', 'post_name' => 'a-note-without-video', 'post_title' => 'A note without a video', 'post_date' => '2026-03-01 10:00:00',
		'post_content' => '<p>Some written tips on collecting flats for a calibration library, with no video in this post at all.</p>'));
	update_option('pms_test_posts_done', 1);
});
