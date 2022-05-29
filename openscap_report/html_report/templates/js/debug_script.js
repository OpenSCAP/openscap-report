
// eslint-disable-next-line no-extend-native
String.prototype.asJqueryComplaintId = function() {
    return this.replace(/\./ug, "");
};

function show_all_rules_details(self) { // eslint-disable-line no-unused-vars
    self.disabled = true;
    var promises = [];
    var selector = "table[id=rule-table] tbody[rule-id] button[id=show_hide_rule_detail_button]";
    document.querySelectorAll(selector).forEach(function (item) {
        var rule_id = item.parentNode.parentNode.parentNode.getAttribute("rule-id").asJqueryComplaintId();
        promises.push(new Promise(resolve => {
            setTimeout(() => {
                resolve(show_rule_detail(item, rule_id)) // eslint-disable-line no-undef
            }, 0.1);
        }));
    });

    Promise.all(promises).then(() => {
        self.disabled = false;
        self.textContent = self.textContent == 'Show all result details' ? 'Hide all result details' : 'Show all result details';
    });
}