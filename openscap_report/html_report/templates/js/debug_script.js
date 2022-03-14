/* eslint-env jquery */

function show_all_rules_details(self) { // eslint-disable-line no-unused-vars
    $("#rule-table tbody[rule-id] button").queue(function (next) { // eslint-disable-line array-callback-return
        setTimeout(() => {
            $(this).click();
        }, 1);
        next();
    });
    self.text((self.text() == 'Show all result details') ? 'Hide all result details' : 'Show all result details');
}