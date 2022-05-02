
// eslint-disable-next-line no-extend-native
String.prototype.asJqueryComplaintId = function() {
    return this.replace(/\./ug, "");
};

function show_all_rules_details(self) { // eslint-disable-line no-unused-vars
    self.setAttribute('disabled', 'disabled');
    const promises = []
    const selector = "table[id=rule-table] tbody[rule-id] button[id=show_hide_rule_detail_button]";
    const rule_buttons = document.querySelectorAll(selector);
    rule_buttons.forEach(function (item) {
        promises.push(new Promise(resolve => {
            setTimeout(() => {
            resolve(show_rule_detail(item)); // eslint-disable-line no-undef
            }, 0.001);
        }))
    });
    Promise.all(promises).then(() => {
        self.textContent = self.textContent == 'Show all result details' ? 'Hide all result details' : 'Show all result details';
        self.removeAttribute('disabled');
    });
}