using System.Windows;
using System.Windows.Controls;
using WpfAppCvoca.ViewModels;

namespace WpfAppCvoca.Views.Steps
{
    /// <summary>
    /// Step0ShowAllView.xaml에 대한 상호 작용 논리
    /// </summary>
    public partial class Step0ShowAllView : UserControl
    {
        private Step0ShowAllViewModel _viewModel;

        public Step0ShowAllView()
        {
            InitializeComponent();
            this.DataContextChanged += Step0ShowAllView_DataContextChanged;
        }

        private void Step0ShowAllView_DataContextChanged(object sender, DependencyPropertyChangedEventArgs e)
        {
            if (_viewModel != null)
            {
                _viewModel.PropertyChanged -= ViewModel_PropertyChanged;
            }

            _viewModel = e.NewValue as Step0ShowAllViewModel;
            if (_viewModel != null)
            {
                _viewModel.PropertyChanged += ViewModel_PropertyChanged;
                UpdateColumnVisibility();
            }
        }

        private void ViewModel_PropertyChanged(object sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(Step0ShowAllViewModel.ShowWordColumn) ||
                e.PropertyName == nameof(Step0ShowAllViewModel.ShowDefinitionColumn) ||
                e.PropertyName == nameof(Step0ShowAllViewModel.ShowExampleColumn) ||
                e.PropertyName == nameof(Step0ShowAllViewModel.LayoutMode))
            {
                UpdateColumnVisibility();
            }
        }

        private void UpdateColumnVisibility()
        {
            if (_viewModel == null || WordDataGrid == null)
                return;

            // DataGrid 컬럼은 인덱스로 접근
            if (WordDataGrid.Columns.Count >= 3)
            {
                WordDataGrid.Columns[0].Visibility = _viewModel.ShowWordColumn 
                    ? Visibility.Visible 
                    : Visibility.Collapsed;
                WordDataGrid.Columns[1].Visibility = _viewModel.ShowDefinitionColumn 
                    ? Visibility.Visible 
                    : Visibility.Collapsed;
                WordDataGrid.Columns[2].Visibility = _viewModel.ShowExampleColumn 
                    ? Visibility.Visible 
                    : Visibility.Collapsed;
            }
        }
    }
}
