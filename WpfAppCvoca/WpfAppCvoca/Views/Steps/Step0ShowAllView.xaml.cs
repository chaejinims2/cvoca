using System.Windows;
using System.Windows.Controls;

namespace WpfAppCvoca.Views.Steps
{
    /// <summary>
    /// Step0ShowAllView.xaml에 대한 상호 작용 논리
    /// </summary>
    public partial class Step0ShowAllView : UserControl
    {
        public Step0ShowAllView()
        {
            InitializeComponent();
            this.Loaded += Step0ShowAllView_Loaded;
            this.DataContextChanged += Step0ShowAllView_DataContextChanged;
        }

        private void Step0ShowAllView_DataContextChanged(object sender, DependencyPropertyChangedEventArgs e)
        {
            if (e.NewValue != null && SpellingDataGrid != null)
            {
                var viewModel = e.NewValue as WpfAppCvoca.ViewModels.MainViewModel;
                if (viewModel != null && SpellingDataGrid.ItemsSource == null && viewModel.SpellingItems != null && viewModel.SpellingItems.Count > 0)
                {
                    SpellingDataGrid.ItemsSource = viewModel.SpellingItems;
                }
            }
        }

        
        private void Step0ShowAllView_Loaded(object sender, RoutedEventArgs e)
        {
            if (this.DataContext != null)
            {
                SetDataGridItemsSource();
            }
            else
            {
                var parent = this.Parent;
                while (parent != null)
                {
                    if (parent is FrameworkElement fe && fe.DataContext != null)
                    {
                        this.DataContext = fe.DataContext;
                        SetDataGridItemsSource();
                        break;
                    }
                    parent = LogicalTreeHelper.GetParent(parent);
                }
            }
        }

        private void SetDataGridItemsSource()
        {
            if (SpellingDataGrid == null)
                return;

            var viewModel = this.DataContext as WpfAppCvoca.ViewModels.MainViewModel;
            if (viewModel == null)
                return;

            if (SpellingDataGrid.ItemsSource == null && viewModel.SpellingItems != null && viewModel.SpellingItems.Count > 0)
            {
                SpellingDataGrid.ItemsSource = viewModel.SpellingItems;
            }
        }
    }
}

