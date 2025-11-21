using System;
using System.Collections.Generic;
using System.Linq;
using WpfAppCvoca.Models;

namespace WpfAppCvoca.Services
{
    /// <summary>
    /// 메모리 캐시를 사용하는 WordRepository 래퍼
    /// 자주 사용되는 데이터를 메모리에 캐시하여 성능 향상
    /// </summary>
    public class CachedWordRepository : IWordRepository
    {
        private readonly IWordRepository _baseRepository;
        
        // 메모리 캐시
        private List<Word> _wordsCache;
        private List<Definition> _definitionsCache;
        private List<Example> _examplesCache;
        private bool _isCacheLoaded = false;
        private readonly object _cacheLock = new object();

        // 내부 데이터 모델 (캐시용)
        private class Word
        {
            public int WordId { get; set; }
            public int DayNo { get; set; }
            public int WordNo { get; set; }
            public string WordText { get; set; }
        }

        private class Definition
        {
            public int DefinitionId { get; set; }
            public int WordId { get; set; }
            public int SenseNo { get; set; }
            public string DefinitionText { get; set; }
            public string PartOfSpeech { get; set; }
        }

        private class Example
        {
            public int ExampleId { get; set; }
            public int DefinitionId { get; set; }
            public int ExampleNo { get; set; }
            public string ExampleSentence { get; set; }
        }

        public CachedWordRepository(IWordRepository baseRepository)
        {
            _baseRepository = baseRepository ?? throw new ArgumentNullException(nameof(baseRepository));
        }

        /// <summary>
        /// 캐시를 초기화합니다. 필요할 때만 호출됩니다.
        /// </summary>
        private void EnsureCacheLoaded()
        {
            if (_isCacheLoaded)
                return;

            lock (_cacheLock)
            {
                if (_isCacheLoaded)
                    return;

                // SQLiteWordRepository에서 직접 로드 (내부 메서드 필요)
                // 또는 별도의 LoadAllRawData 메서드 추가 필요
                LoadCacheFromDatabase();
                _isCacheLoaded = true;
            }
        }

        private void LoadCacheFromDatabase()
        {
            // TODO: SQLiteWordRepository에 LoadAllRawData 메서드 추가 필요
            // 또는 여기서 직접 SQLite 연결하여 로드
            // 현재는 기본 구현으로 두고, 필요시 확장
        }

        /// <summary>
        /// 캐시를 무효화합니다. 데이터가 변경된 후 호출해야 합니다.
        /// </summary>
        public void InvalidateCache()
        {
            lock (_cacheLock)
            {
                _isCacheLoaded = false;
                _wordsCache = null;
                _definitionsCache = null;
                _examplesCache = null;
            }
        }

        // ========== IWordRepository 구현 ==========

        public IEnumerable<SpellingItem> LoadAllWords()
        {
            // 간단한 쿼리는 캐시 없이 직접 호출
            return _baseRepository.LoadAllWords();
        }

        public IEnumerable<SpellingItem> LoadWordsByDay(int dayNo)
        {
            return _baseRepository.LoadWordsByDay(dayNo);
        }

        public int UpdateWord(int wordId, string word)
        {
            var result = _baseRepository.UpdateWord(wordId, word);
            if (result > 0)
            {
                InvalidateCache();
            }
            return result;
        }

        public int UpdateWords(IEnumerable<SpellingItem> words)
        {
            var result = _baseRepository.UpdateWords(words);
            if (result > 0)
            {
                InvalidateCache();
            }
            return result;
        }

        public IEnumerable<WordItem> LoadAllWordItems(LayoutMode layoutMode)
        {
            // 캐시를 사용한 로컬 조인 방식
            EnsureCacheLoaded();

            lock (_cacheLock)
            {
                return BuildWordItemsFromCache(layoutMode);
            }
        }

        private IEnumerable<WordItem> BuildWordItemsFromCache(LayoutMode layoutMode)
        {
            var wordItems = new List<WordItem>();

            switch (layoutMode)
            {
                case LayoutMode.WordOnly:
                    return _wordsCache.Select(w => new WordItem
                    {
                        WordId = w.WordId,
                        DayNo = w.DayNo,
                        WordNo = w.WordNo,
                        Word = w.WordText,
                        DefinitionId = 0,
                        ExampleId = 0,
                        Definition = string.Empty,
                        Example = string.Empty
                    }).OrderBy(x => x.DayNo).ThenBy(x => x.WordNo);

                case LayoutMode.WordDefinition:
                    return from w in _wordsCache
                           join d in _definitionsCache on w.WordId equals d.WordId
                           orderby w.DayNo, w.WordNo, d.SenseNo
                           select new WordItem
                           {
                               WordId = w.WordId,
                               DayNo = w.DayNo,
                               WordNo = w.WordNo,
                               Word = w.WordText,
                               DefinitionId = d.DefinitionId,
                               ExampleId = 0,
                               Definition = d.DefinitionText,
                               Example = string.Empty
                           };

                case LayoutMode.WordDefinitionExample:
                    return from w in _wordsCache
                           join d in _definitionsCache on w.WordId equals d.WordId
                           join e in _examplesCache on d.DefinitionId equals e.DefinitionId
                           orderby w.DayNo, w.WordNo, d.SenseNo, e.ExampleNo
                           select new WordItem
                           {
                               WordId = w.WordId,
                               DayNo = w.DayNo,
                               WordNo = w.WordNo,
                               Word = w.WordText,
                               DefinitionId = d.DefinitionId,
                               ExampleId = e.ExampleId,
                               Definition = d.DefinitionText,
                               Example = e.ExampleSentence
                           };

                // 다른 모드들도 유사하게 구현
                default:
                    // 기본 구현으로 폴백
                    return _baseRepository.LoadAllWordItems(layoutMode);
            }
        }

        public int UpdateWordItemWord(int wordId, string word)
        {
            var result = _baseRepository.UpdateWordItemWord(wordId, word);
            if (result > 0)
            {
                InvalidateCache();
            }
            return result;
        }

        public int UpdateWordItemDefinition(int wordId, string definition)
        {
            var result = _baseRepository.UpdateWordItemDefinition(wordId, definition);
            if (result > 0)
            {
                InvalidateCache();
            }
            return result;
        }

        public int UpdateWordItemExample(int wordId, string example)
        {
            var result = _baseRepository.UpdateWordItemExample(wordId, example);
            if (result > 0)
            {
                InvalidateCache();
            }
            return result;
        }

        public int UpdateWordItems(IEnumerable<WordItem> wordItems)
        {
            var result = _baseRepository.UpdateWordItems(wordItems);
            if (result > 0)
            {
                InvalidateCache();
            }
            return result;
        }
    }
}

