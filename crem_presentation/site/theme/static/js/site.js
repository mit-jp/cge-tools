$ = Bokeh.$;
$(".drawer-button").click(function(){
  $(".drawer").toggleClass('is-visible');
});

Bokeh.custom.form_change = function(form) {
    scenarios = '';
    if ( form.chk_three.checked ) {
        scenarios = scenarios + 'three,';
    }
    if ( form.chk_four.checked ) {
        scenarios = scenarios + 'four,';
    }
    if ( form.chk_five.checked ) {
        scenarios = scenarios + 'five,';
    }
    if ( form.chk_bau.checked ) {
        scenarios = scenarios + 'bau,';
    }
    Bokeh.custom.select_scenario(scenarios);
};
