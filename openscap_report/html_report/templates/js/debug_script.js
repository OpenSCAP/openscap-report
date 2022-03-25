/* eslint-env jquery */

// eslint-disable-next-line no-extend-native
String.prototype.asJqueryComplaintId = function() {
    return this.replace(/\./ug, "");
};

function show_all_rules_details(self) { // eslint-disable-line no-unused-vars
    self.prop('disabled', true);
    var promises = [];
    $("#rule-table tbody[rule-id] button[id=show_hide_rule_detail_button]").queue(function (next) { // eslint-disable-line array-callback-return
        var rule_id = $(this).parent().parent().parent().attr("rule-id").asJqueryComplaintId();
        promises.push(new Promise(resolve => {
            setTimeout(() => {
                // eslint-disable-next-line no-undef
                resolve(show_rule_detail($(this), rule_id))
            }, 0.1);
        }));
        next();
    });

    Promise.all(promises).then(() => {
        self.prop('disabled', false);
        self.text((self.text() == 'Show all result details') ? 'Hide all result details' : 'Show all result details');
    });
}