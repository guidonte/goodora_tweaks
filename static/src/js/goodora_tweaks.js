openerp.goodora_tweaks = function (instance) {

    instance.web.form.FieldPercent = instance.web.form.FieldFloat.extend ({
        template: "FieldPercent",
        widget_class: 'oe_form_field_float oe_form_field_percent',

        format_value: function () {
            return instance.web.format_value (this.get('value') || 0, { type : 'float' }) + '%';
        }
    });

    instance.web.form.widgets.add ('percent', 'instance.web.form.FieldPercent');

    instance.web.list.Percent = instance.web.list.Column.extend ({
        _format: function (row_data, options) {
            var value = row_data[this.id].value;
            if (value) {
                return value + '%';
            }
            return this._super (row_data, options);
        }
    });

    instance.web.list.columns.add ('field.percent', 'instance.web.list.Percent');

};

