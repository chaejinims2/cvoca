using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using WpfAppCvoca.Models;
using WpfAppCvoca.Commands;
using WpfAppCvoca.Services;

namespace WpfAppCvoca.ViewModels
{
    public class Step0ShowAllViewModel : INotifyPropertyChanged
    {
        private readonly IWordRepository _wordRepository;

        public ObservableCollection<WordItem> WordItems { get; } = new ObservableCollection<WordItem>();

        public ObservableCollection<LayoutMode> LayoutModes { get; } = new ObservableCollection<LayoutMode>
        {
            LayoutMode.WordOnly,
            LayoutMode.DefinitionOnly,
            LayoutMode.ExampleOnly,
            LayoutMode.WordDefinition,
            LayoutMode.DefinitionExample,
            LayoutMode.WordDefinitionExample
        };

        private LayoutMode _layoutMode = LayoutMode.WordDefinitionExample;
        public LayoutMode LayoutMode
        {
            get => _layoutMode;
            set
            {
                if (_layoutMode != value)
                {
                    _layoutMode = value;
                    OnPropertyChanged(nameof(LayoutMode));
                    OnPropertyChanged(nameof(ShowWordColumn));
                    OnPropertyChanged(nameof(ShowDefinitionColumn));
                    OnPropertyChanged(nameof(ShowExampleColumn));
                    // 레이아웃 모드가 변경되면 데이터 다시 로드
                    LoadAllWordItems();
                }
            }
        }

        public bool ShowWordColumn
        {
            get => _layoutMode == LayoutMode.WordOnly ||
                   _layoutMode == LayoutMode.WordDefinition ||
                   _layoutMode == LayoutMode.WordDefinitionExample;
        }

        public bool ShowDefinitionColumn
        {
            get => _layoutMode == LayoutMode.DefinitionOnly ||
                   _layoutMode == LayoutMode.WordDefinition ||
                   _layoutMode == LayoutMode.DefinitionExample ||
                   _layoutMode == LayoutMode.WordDefinitionExample;
        }

        public bool ShowExampleColumn
        {
            get => _layoutMode == LayoutMode.ExampleOnly ||
                   _layoutMode == LayoutMode.DefinitionExample ||
                   _layoutMode == LayoutMode.WordDefinitionExample;
        }

        public RelayCommand SaveCommand { get; }

        public Step0ShowAllViewModel() : this(new SQLiteWordRepository())
        {
        }

        public Step0ShowAllViewModel(IWordRepository wordRepository)
        {
            _wordRepository = wordRepository ?? throw new ArgumentNullException(nameof(wordRepository));
            SaveCommand = new RelayCommand(_ => SaveChanges(), _ => WordItems.Count > 0);
            LoadAllWordItems();
        }

        public void LoadAllWordItems()
        {
            WordItems.Clear();

            try
            {
                var items = _wordRepository.LoadAllWordItems(_layoutMode);
                foreach (var item in items)
                {
                    WordItems.Add(item);
                }
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"LoadAllWordItems 오류: {ex.Message}");
                return;
            }

            OnPropertyChanged(nameof(WordItems));
            SaveCommand?.RaiseCanExecuteChanged();
        }

        private void SaveChanges()
        {
            try
            {
                int savedCount = _wordRepository.UpdateWordItems(WordItems);
                System.Diagnostics.Debug.WriteLine($"저장 완료: {savedCount}개 항목");
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"SaveChanges 오류: {ex.Message}");
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged(string name)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }
}
