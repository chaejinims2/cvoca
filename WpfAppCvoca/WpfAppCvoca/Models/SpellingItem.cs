using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WpfAppCvoca.Models
{
    public class SpellingItem : INotifyPropertyChanged
    {
        public int WordId { get; set; }
        public int DayNo { get; set; }
        public int WordNo { get; set; }

        private string _correctSpelling;
        public string CorrectSpelling
        {
            get => _correctSpelling;
            set
            {
                if (_correctSpelling != value)
                {
                    _correctSpelling = value;
                    OnPropertyChanged(nameof(CorrectSpelling));
                }
            }
        }

        private string _userSpelling;
        public string UserSpelling
        {
            get => _userSpelling;
            set
            {
                if (_userSpelling != value)
                {
                    _userSpelling = value;
                    OnPropertyChanged(nameof(UserSpelling));
                }
            }
        }

        private string _resultMark;
        public string ResultMark
        {
            get => _resultMark;
            set
            {
                if (_resultMark != value)
                {
                    _resultMark = value;
                    OnPropertyChanged(nameof(ResultMark));
                }
            }
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