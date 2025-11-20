using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using WpfAppCvoca.Models;
using WpfAppCvoca.Commands;
using WpfAppCvoca.Services;

namespace WpfAppCvoca.ViewModels
{
    public class Step1SpellingsViewModel : INotifyPropertyChanged
    {
        private readonly IWordRepository _wordRepository;

        public ObservableCollection<SpellingItem> SpellingItems { get; } = new ObservableCollection<SpellingItem>();

        private string _spellingSummary;
        public string SpellingSummary
        {
            get => _spellingSummary;
            set
            {
                if (_spellingSummary != value)
                {
                    _spellingSummary = value;
                    OnPropertyChanged(nameof(SpellingSummary));
                    SpellingSummaryChanged?.Invoke(this, EventArgs.Empty);
                }
            }
        }

        public RelayCommand CheckSpellingCommand { get; }
        public RelayCommand SaveCommand { get; }

        public event EventHandler SpellingSummaryChanged;

        public Step1SpellingsViewModel() : this(new SQLiteWordRepository())
        {
        }

        public Step1SpellingsViewModel(IWordRepository wordRepository)
        {
            _wordRepository = wordRepository ?? throw new ArgumentNullException(nameof(wordRepository));
            CheckSpellingCommand = new RelayCommand(_ => CheckSpelling(), _ => SpellingItems.Count > 0);
            SaveCommand = new RelayCommand(_ => SaveSpellingChanges(), _ => SpellingItems.Count > 0);
        }

        public void LoadDaySpelling(int dayNo)
        {
            SpellingItems.Clear();

            try
            {
                var words = _wordRepository.LoadWordsByDay(dayNo);
                foreach (var item in words)
                {
                    SpellingItems.Add(item);
                }
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"LoadDaySpelling 오류: {ex.Message}");
                SpellingSummary = $"오류: {ex.Message}";
                return;
            }

            SpellingSummary = string.Format("정답 0 / {0} (0%)", SpellingItems.Count);
            OnPropertyChanged(nameof(SpellingItems));
            CheckSpellingCommand?.RaiseCanExecuteChanged();
            SaveCommand?.RaiseCanExecuteChanged();
        }

        private void CheckSpelling()
        {
            int total = 0;
            int correct = 0;

            foreach (var item in SpellingItems)
            {
                total++;

                string user = (item.UserSpelling ?? string.Empty).Trim();
                string answer = (item.CorrectSpelling ?? string.Empty).Trim();

                bool isCorrect = string.Equals(user, answer, StringComparison.OrdinalIgnoreCase);

                item.ResultMark = isCorrect ? "O" : "X";
                if (isCorrect)
                    correct++;
            }

            double rate = (total > 0) ? (correct * 100.0 / total) : 0.0;
            SpellingSummary = string.Format("정답 {0} / {1} ({2:0.#}%)", correct, total, rate);
        }

        private void SaveSpellingChanges()
        {
            try
            {
                int savedCount = _wordRepository.UpdateWords(SpellingItems);
                System.Diagnostics.Debug.WriteLine($"저장 완료: {savedCount}개 단어");
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"SaveSpellingChanges 오류: {ex.Message}");
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged(string name)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }
}
