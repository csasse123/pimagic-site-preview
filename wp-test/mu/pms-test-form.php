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
