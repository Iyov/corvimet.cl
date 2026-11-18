jQuery(function($) { 

				jQuery( '.dropdown_product_cat' ).on( 'change', function() {
					if ( jQuery(this).val() != '' ) {
						var this_page = '';
						var home_url  = '/';
						if ( home_url.indexOf( '?' ) > 0 ) {
							this_page = home_url + '&product_cat=' + jQuery(this).val();
						} else {
							this_page = home_url + '?product_cat=' + jQuery(this).val();
						}
						location.href = this_page;
					} else {
						location.href = '/tienda/';
					}
				});

				if ( jQuery().selectWoo ) {
					var wc_product_cat_select = function() {
						jQuery( '.dropdown_product_cat' ).selectWoo( {
							placeholder: 'Select a category',
							minimumResultsForSearch: 5,
							width: '100%',
							allowClear: true,
							language: {
								noResults: function() {
									return 'No matches found';
								}
							}
						} );
					};
					wc_product_cat_select();
				}
			
 });
