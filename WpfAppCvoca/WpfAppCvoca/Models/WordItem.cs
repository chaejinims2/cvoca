using System.ComponentModel;

namespace WpfAppCvoca.Models
{
    /// <summary>
    /// Step 0 (Show All)에서 사용하는 단어 정보 모델
    /// Word, Definition, Example을 포함합니다.
    /// </summary>
    public class WordItem : INotifyPropertyChanged
    {
        public int WordId { get; set; }
        public int DayNo { get; set; }
        public int WordNo { get; set; }
        
        // Primary Key로 사용될 ID들 (레이아웃 모드에 따라 다름)
        public int DefinitionId { get; set; }
        public int ExampleId { get; set; }

        private string _word;
        public string Word
        {
            get => _word;
            set
            {
                if (_word != value)
                {
                    _word = value;
                    OnPropertyChanged(nameof(Word));
                }
            }
        }

        private string _definition;
        public string Definition
        {
            get => _definition;
            set
            {
                if (_definition != value)
                {
                    _definition = value;
                    OnPropertyChanged(nameof(Definition));
                }
            }
        }

        private string _example;
        public string Example
        {
            get => _example;
            set
            {
                if (_example != value)
                {
                    _example = value;
                    OnPropertyChanged(nameof(Example));
                }
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged(string name)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }
}

