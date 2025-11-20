using System;
using System.Globalization;
using System.Windows.Data;

namespace WpfAppCvoca.Converters
{
    public class BoolToThemeTextConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is bool isDarkMode)
            {
                return isDarkMode ? "Light" : "Dark";
            }
            return "Dark";
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}

