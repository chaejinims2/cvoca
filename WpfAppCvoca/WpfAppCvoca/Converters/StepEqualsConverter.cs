using System;
using System.Globalization;
using System.Windows.Data;

namespace WpfAppCvoca.Converters
{
    public class StepEqualsConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value == null || parameter == null)
                return false;

            // value가 int인 경우 직접 사용
            int currentStep;
            if (value is int intValue)
            {
                currentStep = intValue;
            }
            else if (!int.TryParse(value.ToString(), out currentStep))
            {
                return false;
            }

            // parameter는 항상 문자열로 전달됨
            int targetStep;
            if (parameter is int intParam)
            {
                targetStep = intParam;
            }
            else if (!int.TryParse(parameter.ToString(), out targetStep))
            {
                return false;
            }

            return currentStep == targetStep;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            // ToggleButton의 IsChecked에서는 보통 OneWay로만 사용
            return Binding.DoNothing;
        }
    }
}
