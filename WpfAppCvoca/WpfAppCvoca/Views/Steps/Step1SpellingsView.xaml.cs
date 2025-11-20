using System.Windows;
using System.Windows.Controls;

namespace WpfAppCvoca.Views.Steps
{
    /// <summary>
    /// Step1SpellingsView.xaml에 대한 상호 작용 논리
    /// </summary>
    public partial class Step1SpellingsView : UserControl
    {
        public Step1SpellingsView()
        {
            InitializeComponent();
            this.Loaded += Step1SpellingsView_Loaded;
            this.DataContextChanged += Step1SpellingsView_DataContextChanged;
        }

        private void Step1SpellingsView_DataContextChanged(object sender, DependencyPropertyChangedEventArgs e)
        {
            if (e.NewValue != null && SpellingDataGrid != null)
            {
                var viewModel = e.NewValue as WpfAppCvoca.ViewModels.MainViewModel;
                if (viewModel != null && SpellingDataGrid.ItemsSource == null && viewModel.SpellingItems.Count > 0)
                {
                    SpellingDataGrid.ItemsSource = viewModel.SpellingItems;
                }
            }
        }

        private void Step1SpellingsView_Loaded(object sender, RoutedEventArgs e)
        {
            // DataContext가 이미 설정되어 있으면 DataGrid 설정
            if (this.DataContext != null)
            {
                SetDataGridItemsSource();
            }
            else
            {
                // 부모의 DataContext를 찾아서 설정
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

            // ItemsSource가 null이면 수동으로 설정
            if (SpellingDataGrid.ItemsSource == null && viewModel.SpellingItems.Count > 0)
            {
                SpellingDataGrid.ItemsSource = viewModel.SpellingItems;
            }
        }
    }
}
