using System;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Input;
using WpfAppCvoca.ViewModels;
using WpfAppCvoca.Views.Steps;
using System.Windows.Forms;

namespace WpfAppCvoca
{
    public partial class MainWindow : Window
    {
        private MainViewModel _viewModel;

        public MainWindow()
        {
            InitializeComponent();

            this.Loaded += MainWindow_Loaded;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            try
            {
                // 윈도우 위치/크기 설정: 마지막 모니터 사용 (모니터가 여러 개일 때 가장 오른쪽 모니터)
                Screen targetScreen = Screen.AllScreens[Screen.AllScreens.Length - 1];

                var screenWidth = targetScreen.WorkingArea.Width;
                var screenHeight = targetScreen.WorkingArea.Height;
                var screenLeft = targetScreen.WorkingArea.Left;
                var screenTop = targetScreen.WorkingArea.Top;

                this.Width = screenWidth / 5.0;// /2.0;
                this.Height = screenHeight / 5.0 * 4.0 /2.0;
                this.Left = screenLeft;// + screenWidth / 5.0 * 1.0;
                this.Top = screenTop;// + screenHeight / 7.0;

                this.WindowState = WindowState.Normal;
                this.ResizeMode = ResizeMode.CanResize;
                // DataContext 설정
                _viewModel = new MainViewModel();
                this.DataContext = _viewModel;
            }
            catch (TypeInitializationException tex)
            {
                LogException(tex);
                throw; // 원하면 다시 던짐
            }
            catch (Exception ex)
            {
                LogException(ex);
                throw;
            }


            // UserControl들이 생성될 때까지 대기 후 DataContext 설정
            this.Dispatcher.BeginInvoke(new System.Action(() =>
            {
                SetUserControlDataContexts();
            }), System.Windows.Threading.DispatcherPriority.Loaded);
        }

        private void SetUserControlDataContexts()
        {
            // Step 0은 Step0ViewModel을 직접 사용
            if (Step0View != null)
                Step0View.DataContext = _viewModel?.Step0ViewModel;

            // Step 1은 MainViewModel을 통해 프록시 (Step1ViewModel의 속성들을 MainViewModel이 프록시)
            if (Step1View != null)
                Step1View.DataContext = _viewModel;

            if (Step2View != null)
                Step2View.DataContext = _viewModel;

            if (Step3View != null)
                Step3View.DataContext = _viewModel;
        }

        private void TitleBar_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ClickCount == 2)
            {
                ToggleWindowState();
            }
            else
            {
                this.DragMove();
            }
        }

        private void BtnSettings_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Settings window 열기
        }

        private void BtnMinimize_Click(object sender, RoutedEventArgs e)
        {
            this.WindowState = WindowState.Minimized;
        }

        private void BtnMaximize_Click(object sender, RoutedEventArgs e)
        {
            ToggleWindowState();
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        private void ToggleWindowState()
        {
            this.WindowState = this.WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;
        }
        
        private void LogException(Exception ex)
        {
            // 디버그 출력 + 파일 기록
            var full = BuildExceptionChain(ex);
            Debug.WriteLine(full);
            File.WriteAllText("exception_log.txt", full);
        }

        private string BuildExceptionChain(Exception ex)
        {
            var sb = new System.Text.StringBuilder();
            var cur = ex;
            int depth = 0;
            while (cur != null)
            {
                sb.AppendLine($"[{depth}] {cur.GetType().FullName}: {cur.Message}");
                sb.AppendLine(cur.StackTrace ?? "");
                cur = cur.InnerException;
                depth++;
            }
            return sb.ToString();
        }
    }
}