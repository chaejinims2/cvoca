using System;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows;
using WpfAppCvoca.Models;
using WpfAppCvoca.Commands;

namespace WpfAppCvoca.ViewModels
{
    public class MainViewModel : INotifyPropertyChanged
    {
        public ThemeViewModel Theme { get; }

        public static string DbPath
        {
            get
            {
                // 실행 파일 위치의 data 폴더 — AppDomain.CurrentDomain.BaseDirectory를 사용해 더 안정적으로 얻음
                // (Assembly.GetExecutingAssembly().Location은 네트워크/디버그 환경에서 예기치 않은 경로를 반환할 수 있음)
                string baseDir = AppDomain.CurrentDomain.BaseDirectory;
                if (string.IsNullOrEmpty(baseDir))
                {
                    string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location;
                    baseDir = System.IO.Path.GetDirectoryName(exePath) ?? string.Empty;
                }

                string dbPath = System.IO.Path.Combine(baseDir, "data", "ielts_voca_20_30", "ielts_voca_20_30.db");

                // 정규화 및 예외 안전 처리
                try
                {
                    dbPath = System.IO.Path.GetFullPath(dbPath);
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"[DbPath] Path.GetFullPath 실패: {ex.Message}");
                }

                System.Diagnostics.Debug.WriteLine($"[DbPath] Resolved DB path: {dbPath}");

                // 기본 경로에 DB가 없으면 폴백 경로 사용
                try
                {
                    if (!System.IO.File.Exists(dbPath))
                    {
                        string fallbackDir = @"C:\Users\cjim\source\data\ielts_voca_20_30";
                        string fallbackDb = System.IO.Path.Combine(fallbackDir, "ielts_voca_20_30.db");
                        try
                        {
                            fallbackDb = System.IO.Path.GetFullPath(fallbackDb);
                        }
                        catch (Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"[DbPath] Fallback Path.GetFullPath 실패: {ex.Message}");
                        }

                        if (System.IO.File.Exists(fallbackDb))
                        {
                            System.Diagnostics.Debug.WriteLine($"[DbPath] Primary DB not found. Falling back to: {fallbackDb}");
                            return fallbackDb;
                        }
                        else
                        {
                            System.Diagnostics.Debug.WriteLine($"[DbPath] Primary DB not found and fallback not found: {fallbackDb}");
                        }
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"[DbPath] File.Exists 검사 중 예외: {ex.Message}");
                }

                return dbPath;
            }
        }
        private const int MaxDay = 20;

        public string DatabaseFileName
        {
            get
            {
                string dbPath = DbPath;
                if (string.IsNullOrEmpty(dbPath))
                    return "vocabulary.db";
                
                string fileName = System.IO.Path.GetFileName(dbPath);
                return $"{fileName}";
            }
        }
        public string DatabaseName
        {
            // DatabaseFileName에서 확장자를 제거하여 처리
            get
            {
                string fileName = DatabaseFileName;
                return fileName.Split('.')[0];
            }
        }

        public ObservableCollection<int> Days { get; } = new ObservableCollection<int>();

        public Step0ShowAllViewModel Step0ViewModel { get; }
        public Step1SpellingsViewModel Step1ViewModel { get; }

        private int _selectedDay;
        public int SelectedDay
        {
            get => _selectedDay;
            set
            {
                if (_selectedDay != value)
                {
                    _selectedDay = value;
                    OnPropertyChanged(nameof(SelectedDay));
                    
                    // Step 0 (Show All)이 아닐 때만 특정 Day 로드
                    if (_currentStep != 0 && _currentStep == 1)
                    {
                        Step1ViewModel?.LoadDaySpelling(_selectedDay);
                    }
                    UpdateTexts();
                }
            }
        }

        private int _currentStep = 1; // 0: Show All, 1: Spelling, 2: Meanings, 3: Examples
        public int CurrentStep
        {
            get => _currentStep;
            set
            {
                if (_currentStep != value)
                {
                    _currentStep = value;
                    OnPropertyChanged(nameof(CurrentStep));
                    OnPropertyChanged(nameof(SpellingItems));
                    OnPropertyChanged(nameof(CheckSpellingCommand));
                    OnPropertyChanged(nameof(SaveCommand));
                    OnPropertyChanged(nameof(SpellingSummary));
                    UpdateTexts();
                    UpdatePanelVisibility();
                }
            }
        }

        private Visibility _panelStepSpellingsVisibility = Visibility.Collapsed;
        public Visibility PanelStepSpellingsVisibility
        {
            get => _panelStepSpellingsVisibility;
            set
            {
                if (_panelStepSpellingsVisibility != value)
                {
                    _panelStepSpellingsVisibility = value;
                    OnPropertyChanged(nameof(PanelStepSpellingsVisibility));
                }
            }
        }

        private Visibility _panelStepMeaningsVisibility = Visibility.Collapsed;
        public Visibility PanelStepMeaningsVisibility
        {
            get => _panelStepMeaningsVisibility;
            set
            {
                if (_panelStepMeaningsVisibility != value)
                {
                    _panelStepMeaningsVisibility = value;
                    OnPropertyChanged(nameof(PanelStepMeaningsVisibility));
                }
            }
        }

        private Visibility _panelStepExamplesVisibility = Visibility.Collapsed;
        public Visibility PanelStepExamplesVisibility
        {
            get => _panelStepExamplesVisibility;
            set
            {
                if (_panelStepExamplesVisibility != value)
                {
                    _panelStepExamplesVisibility = value;
                    OnPropertyChanged(nameof(PanelStepExamplesVisibility));
                }
            }
        }

        private string _defaultSummary;
        public string DefaultSummary
        {
            get => _defaultSummary;
            set
            {
                if (_defaultSummary != value)
                {
                    _defaultSummary = value;
                    OnPropertyChanged(nameof(DefaultSummary));
                }
            }
        }
        public string SpellingSummary
        {
            get
            {
                if (_currentStep == 0)
                    return Step0ViewModel?.SpellingSummary ?? string.Empty;
                else if (_currentStep == 1)
                    return Step1ViewModel?.SpellingSummary ?? string.Empty;
                return string.Empty;
            }
        }

        private string _stepHeaderText;
        public string StepHeaderText
        {
            get => _stepHeaderText;
            set
            {
                if (_stepHeaderText != value)
                {
                    _stepHeaderText = value;
                    OnPropertyChanged(nameof(StepHeaderText));
                }
            }
        }

        private string _statusBarText;
        public string StatusBarText
        {
            get => _statusBarText;
            set
            {
                if (_statusBarText != value)
                {
                    _statusBarText = value;
                    OnPropertyChanged(nameof(StatusBarText));
                }
            }
        }

        public RelayCommand ChangeStepCommand { get; }

        public RelayCommand CheckSpellingCommand
        {
            get
            {
                if (_currentStep == 0)
                    return Step0ViewModel?.CheckSpellingCommand;
                else if (_currentStep == 1)
                    return Step1ViewModel?.CheckSpellingCommand;
                return null;
            }
        }

        public RelayCommand SaveCommand
        {
            get
            {
                if (_currentStep == 0)
                    return Step0ViewModel?.SaveCommand;
                else if (_currentStep == 1)
                    return Step1ViewModel?.SaveCommand;
                return null;
            }
        }

        public ObservableCollection<SpellingItem> SpellingItems
        {
            get
            {
                if (_currentStep == 0)
                    return Step0ViewModel?.SpellingItems;
                else if (_currentStep == 1)
                    return Step1ViewModel?.SpellingItems;
                return null;
            }
        }

        public MainViewModel()
        {
            // 테마 초기화
            Theme = new ThemeViewModel();

            // Days 채우기
            for (int d = 1; d <= MaxDay; d++)
                Days.Add(d);

            // Step ViewModels 초기화
            Step0ViewModel = new Step0ShowAllViewModel();
            Step0ViewModel.SpellingSummaryChanged += (s, e) => OnPropertyChanged(nameof(SpellingSummary));
            Step0ViewModel.SpellingItems.CollectionChanged += (s, e) => 
            {
                if (_currentStep == 0)
                    OnPropertyChanged(nameof(SpellingItems));
            };
            
            Step1ViewModel = new Step1SpellingsViewModel();
            Step1ViewModel.SpellingSummaryChanged += (s, e) => OnPropertyChanged(nameof(SpellingSummary));
            Step1ViewModel.SpellingItems.CollectionChanged += (s, e) => 
            {
                if (_currentStep == 1)
                    OnPropertyChanged(nameof(SpellingItems));
            };

            // 커맨드 초기화
            ChangeStepCommand = new RelayCommand(p => ChangeStep(p));

            // 초기 데이터 로드
            SelectedDay = 13;
            CurrentStep = 0; // UpdatePanelVisibility가 자동 호출됨
            UpdateTexts();
        }

        private Visibility _panelStepShowAllVisibility = Visibility.Visible;
        public Visibility PanelStepShowAllVisibility
        {
            get => _panelStepShowAllVisibility;
            set
            {
                if (_panelStepShowAllVisibility != value)
                {
                    _panelStepShowAllVisibility = value;
                    OnPropertyChanged(nameof(PanelStepShowAllVisibility));
                }
            }
        }

        private void UpdatePanelVisibility()
        {
            PanelStepShowAllVisibility = (_currentStep == 0) ? Visibility.Visible : Visibility.Collapsed;
            PanelStepSpellingsVisibility = (_currentStep == 1) ? Visibility.Visible : Visibility.Collapsed;
            PanelStepMeaningsVisibility = (_currentStep == 2) ? Visibility.Visible : Visibility.Collapsed;
            PanelStepExamplesVisibility = (_currentStep == 3) ? Visibility.Visible : Visibility.Collapsed;
        }

        private void ChangeStep(object parameter)
        {
            if (parameter == null)
                return;

            int step;
            if (int.TryParse(parameter.ToString(), out step))
            {
                int previousStep = _currentStep;
                CurrentStep = step;
                
                // Step 0 (Show All)일 때 모든 단어 로드
                if (step == 0)
                {
                    Step0ViewModel?.LoadAllWords();
                }
                // Step 1로 변경할 때는 SelectedDay에 맞는 데이터 로드
                else if (step == 1)
                {
                    Step1ViewModel?.LoadDaySpelling(_selectedDay);
                }

                // PropertyChanged를 명시적으로 호출하여 UI 업데이트
                OnPropertyChanged(nameof(SpellingItems));
                OnPropertyChanged(nameof(CheckSpellingCommand));
                OnPropertyChanged(nameof(SaveCommand));
                OnPropertyChanged(nameof(SpellingSummary));
            }
        }


        private void UpdateTexts()
        {
            string stepName = "";
            string stepNameShort = "";

            if (CurrentStep == 0) { stepName = "Show All"; stepNameShort = "Show All"; }
            else if (CurrentStep == 1) { stepName = "Step 1: Spelling"; stepNameShort = "Spelling"; }
            else if (CurrentStep == 2) { stepName = "Step 2: Meanings"; stepNameShort = "Meanings"; }
            else if (CurrentStep == 3) { stepName = "Step 3: Examples"; stepNameShort = "Examples"; }

            if (CurrentStep == 0)
            {
                StepHeaderText = "All Words – " + stepName;
                StatusBarText = string.Format("All Days / {0}", stepNameShort);
            }
            else
            {
                StepHeaderText = string.Format("Day {0} – {1}", SelectedDay, stepName);
                StatusBarText = string.Format("Day {0} / Step {1}: {2}", SelectedDay, CurrentStep, stepNameShort);
            }
            DefaultSummary = string.Format("This is the \"{0}\" default summary", stepName);
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged(string name)
        {
            var handler = PropertyChanged;
            if (handler != null)
                handler(this, new PropertyChangedEventArgs(name));
        }
    }
}
