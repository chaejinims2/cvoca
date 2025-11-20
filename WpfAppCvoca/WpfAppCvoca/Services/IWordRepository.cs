using System.Collections.Generic;
using WpfAppCvoca.Models;

namespace WpfAppCvoca.Services
{
    /// <summary>
    /// 단어 데이터 접근을 위한 Repository 인터페이스
    /// ViewModel은 이 인터페이스에만 의존하여 외부 패키지 의존성을 제거합니다.
    /// </summary>
    public interface IWordRepository
    {
        /// <summary>
        /// 모든 단어를 로드합니다.
        /// </summary>
        /// <returns>단어 목록</returns>
        IEnumerable<SpellingItem> LoadAllWords();

        /// <summary>
        /// 특정 Day의 단어들을 로드합니다.
        /// </summary>
        /// <param name="dayNo">Day 번호</param>
        /// <returns>단어 목록</returns>
        IEnumerable<SpellingItem> LoadWordsByDay(int dayNo);

        /// <summary>
        /// 단어 정보를 업데이트합니다.
        /// </summary>
        /// <param name="wordId">단어 ID</param>
        /// <param name="word">단어</param>
        /// <returns>업데이트된 행 수</returns>
        int UpdateWord(int wordId, string word);

        /// <summary>
        /// 여러 단어를 일괄 업데이트합니다.
        /// </summary>
        /// <param name="words">업데이트할 단어 목록</param>
        /// <returns>업데이트된 행 수</returns>
        int UpdateWords(IEnumerable<SpellingItem> words);

        /// <summary>
        /// 레이아웃 모드에 따라 Word, Definition, Example을 조인하여 모든 단어 정보를 로드합니다.
        /// </summary>
        /// <param name="layoutMode">레이아웃 모드</param>
        /// <returns>단어 정보 목록 (레이아웃 모드에 따라 행 수가 다름)</returns>
        IEnumerable<WordItem> LoadAllWordItems(LayoutMode layoutMode);

        /// <summary>
        /// Word 정보를 업데이트합니다.
        /// </summary>
        /// <param name="wordId">단어 ID</param>
        /// <param name="word">단어</param>
        /// <returns>업데이트된 행 수</returns>
        int UpdateWordItemWord(int wordId, string word);

        /// <summary>
        /// Definition 정보를 업데이트합니다.
        /// </summary>
        /// <param name="wordId">단어 ID</param>
        /// <param name="definition">뜻</param>
        /// <returns>업데이트된 행 수</returns>
        int UpdateWordItemDefinition(int wordId, string definition);

        /// <summary>
        /// Example 정보를 업데이트합니다.
        /// </summary>
        /// <param name="wordId">단어 ID</param>
        /// <param name="example">예문</param>
        /// <returns>업데이트된 행 수</returns>
        int UpdateWordItemExample(int wordId, string example);

        /// <summary>
        /// 여러 WordItem을 일괄 업데이트합니다.
        /// </summary>
        /// <param name="wordItems">업데이트할 단어 정보 목록</param>
        /// <returns>업데이트된 행 수</returns>
        int UpdateWordItems(IEnumerable<WordItem> wordItems);
    }
}

