using System.Windows;
using System.Windows.Controls;

namespace WpfAppCvoca.Views.Steps
{
    /// <summary>
    /// Step3ExamplesView.xaml에 대한 상호 작용 논리
    /// </summary>
    public partial class Step3ExamplesView : UserControl
    {
        public Step3ExamplesView()
        {
            InitializeComponent();
            this.Loaded += Step3ExamplesView_Loaded;
        }

        private void Step3ExamplesView_Loaded(object sender, RoutedEventArgs e)
        {
            // 부모의 DataContext를 찾아서 설정
            var parent = this.Parent;
            while (parent != null)
            {
                if (parent is FrameworkElement fe && fe.DataContext != null)
                {
                    this.DataContext = fe.DataContext;
                    break;
                }
                parent = LogicalTreeHelper.GetParent(parent);
            }
        }
    }
}

