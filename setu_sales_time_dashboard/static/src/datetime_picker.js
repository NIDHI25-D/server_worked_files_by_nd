import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { patch } from "@web/core/utils/patch";
const { DateTime, Info } = luxon;

patch(DateTimePicker.prototype, {
   onPropsUpdated(props) {
       debugger
       super.onPropsUpdated(...arguments);
        const timeValues = this.values.map((val, index) => [
            index === 1 && !this.values[1]
                ? (val || DateTime.local()).hour + 1
                : (val || DateTime.local()).hour,
            val?.minute || Math.floor(DateTime.local().minute / 5) * 5,
            val?.second || 0,
        ]);
        if (props.range) {
            this.state.timeValues = timeValues;
        } else {
            this.state.timeValues = [];
            this.state.timeValues[props.focusedDateIndex] = timeValues[props.focusedDateIndex];
        }

        this.shouldAdjustFocusDate = !props.range;
        this.adjustFocus(this.values, props.focusedDateIndex);
        this.handle12HourSystem();
        this.state.timeValues = this.state.timeValues.map((timeValue) => timeValue.map(String)
        );
   }
 });

