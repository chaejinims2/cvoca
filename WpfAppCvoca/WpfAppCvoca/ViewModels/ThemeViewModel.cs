using System;
using System.ComponentModel;
using System.Windows;
using System.Windows.Media;
using WpfAppCvoca.Commands;

namespace WpfAppCvoca.ViewModels
{
    public enum ThemeMode
    {
        Light,
        Dark
    }

    public class ThemeViewModel : INotifyPropertyChanged
    {
        // VSCode Dark Theme 색상 상수
        private static class DarkColors
        {
            public static readonly Color Background = Color.FromRgb(0x1E, 0x1E, 0x1E);
            public static readonly Color SecondaryBackground = Color.FromRgb(0x25, 0x25, 0x26);
            public static readonly Color Border = Color.FromRgb(0x3C, 0x3C, 0x3C);
            public static readonly Color Accent = Color.FromRgb(0x00, 0x7A, 0xCC);
            public static readonly Color DataGridRow = Color.FromRgb(0x2D, 0x2D, 0x30);
            public static readonly Color DataGridHeader = Color.FromRgb(0x33, 0x33, 0x33);
            public static readonly Color ScrollBarBackground = Color.FromRgb(0x25, 0x25, 0x26);
            public static readonly Color ScrollBarThumb = Color.FromRgb(0x3F, 0x3F, 0x46);
            public static readonly Color ScrollBarThumbHover = Color.FromRgb(0x5A, 0x5A, 0x5F);
            public static readonly Color StatusBar = Color.FromRgb(0x2D, 0x2D, 0x30);
            public static readonly Color Button = Color.FromRgb(0x3A, 0x3D, 0x41);
            public static readonly Color ComboBox = Color.FromRgb(0x2D, 0x2D, 0x30);
            public static readonly Color ToggleButton = Color.FromRgb(0x3A, 0x3D, 0x41);
        }

        // Light Theme 색상 상수
        private static class LightColors
        {
            public static readonly Color Background = Colors.White;
            public static readonly Color SecondaryBackground = Color.FromRgb(0xFD, 0xFD, 0xFD);
            public static readonly Color Border = Color.FromRgb(0xD3, 0xD3, 0xD3);
            public static readonly Color Accent = Color.FromRgb(0x00, 0x78, 0xD7);
            public static readonly Color DataGridRow = Colors.White;
            public static readonly Color DataGridHeader = Color.FromRgb(0xF0, 0xF0, 0xF0);
            public static readonly Color ScrollBarBackground = Color.FromRgb(0xF0, 0xF0, 0xF0);
            public static readonly Color ScrollBarThumb = Color.FromRgb(0xC8, 0xC8, 0xC8);
            public static readonly Color ScrollBarThumbHover = Color.FromRgb(0xB4, 0xB4, 0xB4);
            public static readonly Color StatusBar = Color.FromRgb(0xF0, 0xF0, 0xF0);
            public static readonly Color Button = Color.FromRgb(0xF0, 0xF0, 0xF0);
            public static readonly Color ComboBox = Colors.White;
            public static readonly Color ToggleButton = Color.FromRgb(0xF0, 0xF0, 0xF0);
        }

        private ThemeMode _currentTheme = ThemeMode.Light;

        // Helper 메서드: Color를 SolidColorBrush로 변환
        private static SolidColorBrush Brush(Color color) => new SolidColorBrush(color);

        public ThemeMode CurrentTheme
        {
            get => _currentTheme;
            set
            {
                if (_currentTheme != value)
                {
                    _currentTheme = value;
                    OnPropertyChanged(nameof(CurrentTheme));
                    OnPropertyChanged(nameof(IsDarkMode));
                    OnPropertyChanged(nameof(IsLightMode));
                    UpdateThemeColors();
                }
            }
        }

        public bool IsDarkMode
        {
            get => _currentTheme == ThemeMode.Dark;
            set
            {
                if (value)
                    CurrentTheme = ThemeMode.Dark;
            }
        }

        public bool IsLightMode
        {
            get => _currentTheme == ThemeMode.Light;
            set
            {
                if (value)
                    CurrentTheme = ThemeMode.Light;
            }
        }

        // 배경색
        private Brush _backgroundColor;
        public Brush BackgroundColor
        {
            get => _backgroundColor;
            set
            {
                if (_backgroundColor != value)
                {
                    _backgroundColor = value;
                    OnPropertyChanged(nameof(BackgroundColor));
                }
            }
        }

        // 전경색 (텍스트)
        private Brush _foregroundColor;
        public Brush ForegroundColor
        {
            get => _foregroundColor;
            set
            {
                if (_foregroundColor != value)
                {
                    _foregroundColor = value;
                    OnPropertyChanged(nameof(ForegroundColor));
                }
            }
        }

        // 보조 배경색
        private Brush _secondaryBackgroundColor;
        public Brush SecondaryBackgroundColor
        {
            get => _secondaryBackgroundColor;
            set
            {
                if (_secondaryBackgroundColor != value)
                {
                    _secondaryBackgroundColor = value;
                    OnPropertyChanged(nameof(SecondaryBackgroundColor));
                }
            }
        }

        // 테두리 색상
        private Brush _borderColor;
        public Brush BorderColor
        {
            get => _borderColor;
            set
            {
                if (_borderColor != value)
                {
                    _borderColor = value;
                    OnPropertyChanged(nameof(BorderColor));
                }
            }
        }

        // 강조 색상
        private Brush _accentColor;
        public Brush AccentColor
        {
            get => _accentColor;
            set
            {
                if (_accentColor != value)
                {
                    _accentColor = value;
                    OnPropertyChanged(nameof(AccentColor));
                }
            }
        }

        // DataGrid 배경색
        private Brush _dataGridBackgroundColor;
        public Brush DataGridBackgroundColor
        {
            get => _dataGridBackgroundColor;
            set
            {
                if (_dataGridBackgroundColor != value)
                {
                    _dataGridBackgroundColor = value;
                    OnPropertyChanged(nameof(DataGridBackgroundColor));
                }
            }
        }

        // DataGrid 전경색
        private Brush _dataGridForegroundColor;
        public Brush DataGridForegroundColor
        {
            get => _dataGridForegroundColor;
            set
            {
                if (_dataGridForegroundColor != value)
                {
                    _dataGridForegroundColor = value;
                    OnPropertyChanged(nameof(DataGridForegroundColor));
                }
            }
        }

        // DataGrid 행 배경색
        private Brush _dataGridRowBackgroundColor;
        public Brush DataGridRowBackgroundColor
        {
            get => _dataGridRowBackgroundColor;
            set
            {
                if (_dataGridRowBackgroundColor != value)
                {
                    _dataGridRowBackgroundColor = value;
                    OnPropertyChanged(nameof(DataGridRowBackgroundColor));
                }
            }
        }

        // DataGrid 헤더 배경색
        private Brush _dataGridHeaderBackgroundColor;
        public Brush DataGridHeaderBackgroundColor
        {
            get => _dataGridHeaderBackgroundColor;
            set
            {
                if (_dataGridHeaderBackgroundColor != value)
                {
                    _dataGridHeaderBackgroundColor = value;
                    OnPropertyChanged(nameof(DataGridHeaderBackgroundColor));
                }
            }
        }

        // DataGrid 헤더 전경색
        private Brush _dataGridHeaderForegroundColor;
        public Brush DataGridHeaderForegroundColor
        {
            get => _dataGridHeaderForegroundColor;
            set
            {
                if (_dataGridHeaderForegroundColor != value)
                {
                    _dataGridHeaderForegroundColor = value;
                    OnPropertyChanged(nameof(DataGridHeaderForegroundColor));
                }
            }
        }

        // ScrollBar 배경색
        private Brush _scrollBarBackgroundColor;
        public Brush ScrollBarBackgroundColor
        {
            get => _scrollBarBackgroundColor;
            set
            {
                if (_scrollBarBackgroundColor != value)
                {
                    _scrollBarBackgroundColor = value;
                    OnPropertyChanged(nameof(ScrollBarBackgroundColor));
                }
            }
        }

        // ScrollBar Thumb 색상
        private Brush _scrollBarThumbColor;
        public Brush ScrollBarThumbColor
        {
            get => _scrollBarThumbColor;
            set
            {
                if (_scrollBarThumbColor != value)
                {
                    _scrollBarThumbColor = value;
                    OnPropertyChanged(nameof(ScrollBarThumbColor));
                }
            }
        }

        // ScrollBar Thumb Hover 색상
        private Brush _scrollBarThumbHoverColor;
        public Brush ScrollBarThumbHoverColor
        {
            get => _scrollBarThumbHoverColor;
            set
            {
                if (_scrollBarThumbHoverColor != value)
                {
                    _scrollBarThumbHoverColor = value;
                    OnPropertyChanged(nameof(ScrollBarThumbHoverColor));
                }
            }
        }

        // StatusBar 배경색
        private Brush _statusBarBackgroundColor;
        public Brush StatusBarBackgroundColor
        {
            get => _statusBarBackgroundColor;
            set
            {
                if (_statusBarBackgroundColor != value)
                {
                    _statusBarBackgroundColor = value;
                    OnPropertyChanged(nameof(StatusBarBackgroundColor));
                }
            }
        }

        // Button 배경색
        private Brush _buttonBackgroundColor;
        public Brush ButtonBackgroundColor
        {
            get => _buttonBackgroundColor;
            set
            {
                if (_buttonBackgroundColor != value)
                {
                    _buttonBackgroundColor = value;
                    OnPropertyChanged(nameof(ButtonBackgroundColor));
                }
            }
        }

        // Button 전경색
        private Brush _buttonForegroundColor;
        public Brush ButtonForegroundColor
        {
            get => _buttonForegroundColor;
            set
            {
                if (_buttonForegroundColor != value)
                {
                    _buttonForegroundColor = value;
                    OnPropertyChanged(nameof(ButtonForegroundColor));
                }
            }
        }

        // ComboBox 배경색
        private Brush _comboBoxBackgroundColor;
        public Brush ComboBoxBackgroundColor
        {
            get => _comboBoxBackgroundColor;
            set
            {
                if (_comboBoxBackgroundColor != value)
                {
                    _comboBoxBackgroundColor = value;
                    OnPropertyChanged(nameof(ComboBoxBackgroundColor));
                }
            }
        }

        // ComboBox 전경색
        private Brush _comboBoxForegroundColor;
        public Brush ComboBoxForegroundColor
        {
            get => _comboBoxForegroundColor;
            set
            {
                if (_comboBoxForegroundColor != value)
                {
                    _comboBoxForegroundColor = value;
                    OnPropertyChanged(nameof(ComboBoxForegroundColor));
                }
            }
        }

        // ToggleButton 배경색
        private Brush _toggleButtonBackgroundColor;
        public Brush ToggleButtonBackgroundColor
        {
            get => _toggleButtonBackgroundColor;
            set
            {
                if (_toggleButtonBackgroundColor != value)
                {
                    _toggleButtonBackgroundColor = value;
                    OnPropertyChanged(nameof(ToggleButtonBackgroundColor));
                }
            }
        }

        // ToggleButton 전경색
        private Brush _toggleButtonForegroundColor;
        public Brush ToggleButtonForegroundColor
        {
            get => _toggleButtonForegroundColor;
            set
            {
                if (_toggleButtonForegroundColor != value)
                {
                    _toggleButtonForegroundColor = value;
                    OnPropertyChanged(nameof(ToggleButtonForegroundColor));
                }
            }
        }

        public RelayCommand ToggleThemeCommand { get; }

        public ThemeViewModel()
        {
            ToggleThemeCommand = new RelayCommand(_ => ToggleTheme());
            UpdateThemeColors();
        }

        private void ToggleTheme()
        {
            CurrentTheme = CurrentTheme == ThemeMode.Light ? ThemeMode.Dark : ThemeMode.Light;
        }

        private void UpdateThemeColors()
        {
            if (_currentTheme == ThemeMode.Dark)
            {
                BackgroundColor = Brush(DarkColors.Background);
                ForegroundColor = Brushes.White;
                SecondaryBackgroundColor = Brush(DarkColors.SecondaryBackground);
                BorderColor = Brush(DarkColors.Border);
                AccentColor = Brush(DarkColors.Accent);
                DataGridBackgroundColor = Brush(DarkColors.Background);
                DataGridForegroundColor = Brushes.White;
                DataGridRowBackgroundColor = Brush(DarkColors.DataGridRow);
                DataGridHeaderBackgroundColor = Brush(DarkColors.DataGridHeader);
                DataGridHeaderForegroundColor = Brushes.White;
                ScrollBarBackgroundColor = Brush(DarkColors.ScrollBarBackground);
                ScrollBarThumbColor = Brush(DarkColors.ScrollBarThumb);
                ScrollBarThumbHoverColor = Brush(DarkColors.ScrollBarThumbHover);
                StatusBarBackgroundColor = Brush(DarkColors.StatusBar);
                ButtonBackgroundColor = Brush(DarkColors.Button);
                ButtonForegroundColor = Brushes.White;
                ComboBoxBackgroundColor = Brush(DarkColors.ComboBox);
                ComboBoxForegroundColor = Brushes.White;
                ToggleButtonBackgroundColor = Brush(DarkColors.ToggleButton);
                ToggleButtonForegroundColor = Brushes.White;
            }
            else // Light
            {
                BackgroundColor = Brush(LightColors.Background);
                ForegroundColor = Brush(Colors.Black);
                SecondaryBackgroundColor = Brush(LightColors.SecondaryBackground);
                BorderColor = Brush(LightColors.Border);
                AccentColor = Brush(LightColors.Accent);
                DataGridBackgroundColor = Brush(LightColors.DataGridRow);
                DataGridForegroundColor = Brush(Colors.Black);
                DataGridRowBackgroundColor = Brush(LightColors.DataGridRow);
                DataGridHeaderBackgroundColor = Brush(LightColors.DataGridHeader);
                DataGridHeaderForegroundColor = Brush(Colors.Black);
                ScrollBarBackgroundColor = Brush(LightColors.ScrollBarBackground);
                ScrollBarThumbColor = Brush(LightColors.ScrollBarThumb);
                ScrollBarThumbHoverColor = Brush(LightColors.ScrollBarThumbHover);
                StatusBarBackgroundColor = Brush(LightColors.StatusBar);
                ButtonBackgroundColor = Brush(LightColors.Button);
                ButtonForegroundColor = Brush(Colors.Black);
                ComboBoxBackgroundColor = Brush(LightColors.ComboBox);
                ComboBoxForegroundColor = Brush(Colors.Black);
                ToggleButtonBackgroundColor = Brush(LightColors.ToggleButton);
                ToggleButtonForegroundColor = Brush(Colors.Black);
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged(string name)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }
}

