using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.Linq;
using WpfAppCvoca.Models;
using WpfAppCvoca.ViewModels;

namespace WpfAppCvoca.Services
{
    /// <summary>
    /// SQLite를 사용한 WordRepository 구현체
    /// System.Data.SQLite 의존성을 이 클래스에만 격리합니다.
    /// </summary>
    public class SQLiteWordRepository : IWordRepository
    {
        private string GetDbPath()
        {
            return MainViewModel.DbPath;
        }

        public IEnumerable<SpellingItem> LoadAllWords()
        {
            var words = new List<SpellingItem>();
            string dbPath = GetDbPath();

            if (!System.IO.File.Exists(dbPath))
            {
                System.Diagnostics.Debug.WriteLine($"데이터베이스 파일을 찾을 수 없습니다: {dbPath}");
                return words;
            }

            try
            {
                using (var conn = new SQLiteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();

                    using (var cmd = conn.CreateCommand())
                    {
                        cmd.CommandText = SQLiteQueries.LoadAllWords;

                        using (var reader = cmd.ExecuteReader())
                        {
                            while (reader.Read())
                            {
                                words.Add(new SpellingItem
                                {
                                    WordId = reader.GetInt32(0),
                                    DayNo = reader.GetInt32(1),
                                    WordNo = reader.GetInt32(2),
                                    CorrectSpelling = reader.GetString(3),
                                    UserSpelling = string.Empty,
                                    ResultMark = string.Empty
                                });
                            }
                        }
                    }
                }

                System.Diagnostics.Debug.WriteLine($"모든 단어 로드 완료: {words.Count}개 단어");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"LoadAllWords 오류: {ex.Message}");
                throw;
            }

            return words;
        }

        public IEnumerable<SpellingItem> LoadWordsByDay(int dayNo)
        {
            var words = new List<SpellingItem>();
            string dbPath = GetDbPath();

            if (!System.IO.File.Exists(dbPath))
            {
                System.Diagnostics.Debug.WriteLine($"데이터베이스 파일을 찾을 수 없습니다: {dbPath}");
                return words;
            }

            try
            {
                using (var conn = new SQLiteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();

                    using (var cmd = conn.CreateCommand())
                    {
                        cmd.CommandText = SQLiteQueries.LoadWordsByDay;
                        cmd.Parameters.AddWithValue("@day_no", dayNo);

                        using (var reader = cmd.ExecuteReader())
                        {
                            while (reader.Read())
                            {
                                words.Add(new SpellingItem
                                {
                                    WordId = reader.GetInt32(0),
                                    DayNo = reader.GetInt32(1),
                                    WordNo = reader.GetInt32(2),
                                    CorrectSpelling = reader.GetString(3),
                                    UserSpelling = string.Empty,
                                    ResultMark = string.Empty
                                });
                            }
                        }
                    }
                }

                System.Diagnostics.Debug.WriteLine($"Day {dayNo} 로드 완료: {words.Count}개 단어");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"LoadWordsByDay 오류: {ex.Message}");
                throw;
            }

            return words;
        }

        public int UpdateWord(int wordId, string word)
        {
            if (string.IsNullOrEmpty(word))
                return 0;

            string dbPath = GetDbPath();
            if (!System.IO.File.Exists(dbPath))
            {
                System.Diagnostics.Debug.WriteLine($"데이터베이스 파일을 찾을 수 없습니다: {dbPath}");
                return 0;
            }

            try
            {
                using (var conn = new SQLiteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();

                    using (var cmd = conn.CreateCommand())
                    {
                        cmd.CommandText = SQLiteQueries.UpdateWord;
                        cmd.Parameters.AddWithValue("@word", word);
                        cmd.Parameters.AddWithValue("@word_id", wordId);

                        return cmd.ExecuteNonQuery();
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"UpdateWord 오류: {ex.Message}");
                throw;
            }
        }

        public int UpdateWords(IEnumerable<SpellingItem> words)
        {
            if (words == null)
                return 0;

            var wordsToUpdate = words.Where(w => !string.IsNullOrEmpty(w.CorrectSpelling)).ToList();
            if (wordsToUpdate.Count == 0)
                return 0;

            string dbPath = GetDbPath();
            if (!System.IO.File.Exists(dbPath))
            {
                System.Diagnostics.Debug.WriteLine($"데이터베이스 파일을 찾을 수 없습니다: {dbPath}");
                return 0;
            }

            try
            {
                int savedCount = 0;
                using (var conn = new SQLiteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();

                    using (var transaction = conn.BeginTransaction())
                    {
                        using (var cmd = conn.CreateCommand())
                        {
                            cmd.CommandText = SQLiteQueries.UpdateWord;

                            foreach (var item in wordsToUpdate)
                            {
                                cmd.Parameters.Clear();
                                cmd.Parameters.AddWithValue("@word", item.CorrectSpelling);
                                cmd.Parameters.AddWithValue("@word_id", item.WordId);
                                cmd.ExecuteNonQuery();
                                savedCount++;
                            }
                        }
                        transaction.Commit();
                    }
                }

                System.Diagnostics.Debug.WriteLine($"저장 완료: {savedCount}개 단어");
                return savedCount;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"UpdateWords 오류: {ex.Message}");
                throw;
            }
        }

        public IEnumerable<WordItem> LoadAllWordItems(LayoutMode layoutMode)
        {
            var wordItems = new List<WordItem>();
            string dbPath = GetDbPath();

            if (!System.IO.File.Exists(dbPath))
            {
                System.Diagnostics.Debug.WriteLine($"데이터베이스 파일을 찾을 수 없습니다: {dbPath}");
                return wordItems;
            }

            try
            {
                using (var conn = new SQLiteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();

                    using (var cmd = conn.CreateCommand())
                    {
                        // 레이아웃 모드에 따라 다른 쿼리 실행
                        switch (layoutMode)
                        {
                            case LayoutMode.WordOnly:
                                cmd.CommandText = SQLiteQueries.LoadWordOnly;
                                break;

                            case LayoutMode.DefinitionOnly:
                                cmd.CommandText = SQLiteQueries.LoadDefinitionOnly;
                                break;

                            case LayoutMode.ExampleOnly:
                                cmd.CommandText = SQLiteQueries.LoadExampleOnly;
                                break;

                            case LayoutMode.WordDefinition:
                                cmd.CommandText = SQLiteQueries.LoadWordDefinition;
                                break;

                            case LayoutMode.DefinitionExample:
                                cmd.CommandText = SQLiteQueries.LoadDefinitionExample;
                                break;

                            case LayoutMode.WordDefinitionExample:
                                cmd.CommandText = SQLiteQueries.LoadWordDefinitionExample;
                                break;
                        }

                        using (var reader = cmd.ExecuteReader())
                        {
                            while (reader.Read())
                            {
                                wordItems.Add(new WordItem
                                {
                                    WordId = reader.GetInt32(0),
                                    DayNo = reader.GetInt32(1),
                                    WordNo = reader.GetInt32(2),
                                    Word = reader.IsDBNull(3) ? string.Empty : reader.GetString(3),
                                    DefinitionId = reader.GetInt32(4),
                                    ExampleId = reader.GetInt32(5),
                                    Definition = reader.IsDBNull(6) ? string.Empty : reader.GetString(6),
                                    Example = reader.IsDBNull(7) ? string.Empty : reader.GetString(7)
                                });
                            }
                        }
                    }
                }

                System.Diagnostics.Debug.WriteLine($"레이아웃 모드 {layoutMode}로 단어 정보 로드 완료: {wordItems.Count}개");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"LoadAllWordItems 오류: {ex.Message}");
                throw;
            }

            return wordItems;
        }

        public int UpdateWordItemWord(int wordId, string word)
        {
            return UpdateWord(wordId, word);
        }

        public int UpdateWordItemDefinition(int wordId, string definition)
        {
            if (string.IsNullOrEmpty(definition))
                return 0;

            string dbPath = GetDbPath();
            if (!System.IO.File.Exists(dbPath))
            {
                System.Diagnostics.Debug.WriteLine($"데이터베이스 파일을 찾을 수 없습니다: {dbPath}");
                return 0;
            }

            try
            {
                using (var conn = new SQLiteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();

                    using (var cmd = conn.CreateCommand())
                    {
                        cmd.CommandText = SQLiteQueries.UpdateWordItemDefinition;
                        cmd.Parameters.AddWithValue("@definition", definition);
                        cmd.Parameters.AddWithValue("@word_id", wordId);

                        return cmd.ExecuteNonQuery();
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"UpdateWordItemDefinition 오류: {ex.Message}");
                throw;
            }
        }

        public int UpdateWordItemExample(int wordId, string example)
        {
            if (string.IsNullOrEmpty(example))
                return 0;

            string dbPath = GetDbPath();
            if (!System.IO.File.Exists(dbPath))
            {
                System.Diagnostics.Debug.WriteLine($"데이터베이스 파일을 찾을 수 없습니다: {dbPath}");
                return 0;
            }

            try
            {
                using (var conn = new SQLiteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();

                    using (var cmd = conn.CreateCommand())
                    {
                        cmd.CommandText = SQLiteQueries.UpdateWordItemExample;
                        cmd.Parameters.AddWithValue("@example", example);
                        cmd.Parameters.AddWithValue("@word_id", wordId);

                        return cmd.ExecuteNonQuery();
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"UpdateWordItemExample 오류: {ex.Message}");
                throw;
            }
        }

        public int UpdateWordItems(IEnumerable<WordItem> wordItems)
        {
            if (wordItems == null)
                return 0;

            var itemsToUpdate = wordItems.ToList();
            if (itemsToUpdate.Count == 0)
                return 0;

            string dbPath = GetDbPath();
            if (!System.IO.File.Exists(dbPath))
            {
                System.Diagnostics.Debug.WriteLine($"데이터베이스 파일을 찾을 수 없습니다: {dbPath}");
                return 0;
            }

            try
            {
                int savedCount = 0;
                using (var conn = new SQLiteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();

                    using (var transaction = conn.BeginTransaction())
                    {
                        using (var cmd = conn.CreateCommand())
                        {
                            foreach (var item in itemsToUpdate)
                            {
                                // Word 업데이트
                                if (!string.IsNullOrEmpty(item.Word))
                                {
                                    cmd.CommandText = @"
                                        UPDATE words
                                        SET word = @word
                                        WHERE word_id = @word_id;
                                    ";
                                    cmd.Parameters.Clear();
                                    cmd.Parameters.AddWithValue("@word", item.Word);
                                    cmd.Parameters.AddWithValue("@word_id", item.WordId);
                                    cmd.ExecuteNonQuery();
                                    savedCount++;
                                }

                                // Definition 업데이트
                                if (!string.IsNullOrEmpty(item.Definition))
                                {
                                    cmd.CommandText = @"
                                        UPDATE definitions
                                        SET definition = @definition
                                        WHERE definition_id = (
                                            SELECT definition_id 
                                            FROM definitions 
                                            WHERE word_id = @word_id 
                                            ORDER BY sense_no 
                                            LIMIT 1
                                        );
                                    ";
                                    cmd.Parameters.Clear();
                                    cmd.Parameters.AddWithValue("@definition", item.Definition);
                                    cmd.Parameters.AddWithValue("@word_id", item.WordId);
                                    cmd.ExecuteNonQuery();
                                    savedCount++;
                                }

                                // Example 업데이트
                                if (!string.IsNullOrEmpty(item.Example))
                                {
                                    cmd.CommandText = @"
                                        UPDATE examples
                                        SET example_sentence = @example
                                        WHERE example_id = (
                                            SELECT e.example_id
                                            FROM examples e
                                            JOIN definitions d ON e.definition_id = d.definition_id
                                            WHERE d.word_id = @word_id
                                            ORDER BY d.sense_no, e.example_no
                                            LIMIT 1
                                        );
                                    ";
                                    cmd.Parameters.Clear();
                                    cmd.Parameters.AddWithValue("@example", item.Example);
                                    cmd.Parameters.AddWithValue("@word_id", item.WordId);
                                    cmd.ExecuteNonQuery();
                                    savedCount++;
                                }
                            }
                        }
                        transaction.Commit();
                    }
                }

                System.Diagnostics.Debug.WriteLine($"저장 완료: {savedCount}개 항목");
                return savedCount;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"UpdateWordItems 오류: {ex.Message}");
                throw;
            }
        }
    }
}

