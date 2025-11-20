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
                        cmd.CommandText = @"
                            SELECT word_id, day_no, word_no, word
                            FROM words
                            ORDER BY day_no, word_no;
                        ";

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
                        cmd.CommandText = @"
                            SELECT word_id, day_no, word_no, word
                            FROM words
                            WHERE day_no = @day_no
                            ORDER BY word_no;
                        ";
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
                        cmd.CommandText = @"
                            UPDATE words
                            SET word = @word
                            WHERE word_id = @word_id;
                        ";
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
                            cmd.CommandText = @"
                                UPDATE words
                                SET word = @word
                                WHERE word_id = @word_id;
                            ";

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
                                // Word Only: words 테이블만, PK: WordId
                                cmd.CommandText = @"
                                    SELECT 
                                        w.word_id,
                                        w.day_no,
                                        w.word_no,
                                        w.word,
                                        0 as definition_id,
                                        0 as example_id,
                                        '' as definition,
                                        '' as example
                                    FROM words w
                                    ORDER BY w.day_no, w.word_no;
                                ";
                                break;

                            case LayoutMode.DefinitionOnly:
                                // Definition Only: definitions 테이블만, PK: DefinitionId
                                cmd.CommandText = @"
                                    SELECT 
                                        d.word_id,
                                        COALESCE(w.day_no, 0) as day_no,
                                        COALESCE(w.word_no, 0) as word_no,
                                        COALESCE(w.word, '') as word,
                                        d.definition_id,
                                        0 as example_id,
                                        d.definition,
                                        '' as example
                                    FROM definitions d
                                    LEFT JOIN words w ON d.word_id = w.word_id
                                    ORDER BY d.word_id, d.sense_no;
                                ";
                                break;

                            case LayoutMode.ExampleOnly:
                                // Example Only: examples 테이블만, PK: ExampleId
                                cmd.CommandText = @"
                                    SELECT 
                                        COALESCE(d.word_id, 0) as word_id,
                                        COALESCE(w.day_no, 0) as day_no,
                                        COALESCE(w.word_no, 0) as word_no,
                                        COALESCE(w.word, '') as word,
                                        d.definition_id,
                                        e.example_id,
                                        COALESCE(d.definition, '') as definition,
                                        e.example_sentence as example
                                    FROM examples e
                                    LEFT JOIN definitions d ON e.definition_id = d.definition_id
                                    LEFT JOIN words w ON d.word_id = w.word_id
                                    ORDER BY e.example_id;
                                ";
                                break;

                            case LayoutMode.WordDefinition:
                                // Word + Definition: words와 definitions 조인, PK: DefinitionId
                                cmd.CommandText = @"
                                    SELECT 
                                        w.word_id,
                                        w.day_no,
                                        w.word_no,
                                        w.word,
                                        d.definition_id,
                                        0 as example_id,
                                        d.definition,
                                        '' as example
                                    FROM words w
                                    INNER JOIN definitions d ON w.word_id = d.word_id
                                    ORDER BY w.day_no, w.word_no, d.sense_no;
                                ";
                                break;

                            case LayoutMode.DefinitionExample:
                                // Definition + Example: definitions와 examples 조인, PK: ExampleId
                                cmd.CommandText = @"
                                    SELECT 
                                        COALESCE(d.word_id, 0) as word_id,
                                        COALESCE(w.day_no, 0) as day_no,
                                        COALESCE(w.word_no, 0) as word_no,
                                        COALESCE(w.word, '') as word,
                                        d.definition_id,
                                        e.example_id,
                                        d.definition,
                                        e.example_sentence as example
                                    FROM definitions d
                                    INNER JOIN examples e ON d.definition_id = e.definition_id
                                    LEFT JOIN words w ON d.word_id = w.word_id
                                    ORDER BY d.word_id, d.sense_no, e.example_no;
                                ";
                                break;

                            case LayoutMode.WordDefinitionExample:
                                // Word + Definition + Example: words, definitions, examples 조인, PK: ExampleId
                                cmd.CommandText = @"
                                    SELECT 
                                        w.word_id,
                                        w.day_no,
                                        w.word_no,
                                        w.word,
                                        d.definition_id,
                                        e.example_id,
                                        d.definition,
                                        e.example_sentence as example
                                    FROM words w
                                    INNER JOIN definitions d ON w.word_id = d.word_id
                                    INNER JOIN examples e ON d.definition_id = e.definition_id
                                    ORDER BY w.day_no, w.word_no, d.sense_no, e.example_no;
                                ";
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
                        // word_id에 해당하는 첫 번째 definition을 업데이트
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
                        // word_id에 해당하는 첫 번째 definition의 첫 번째 example을 업데이트
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
                        foreach (var item in itemsToUpdate)
                        {
                            // Word 업데이트
                            if (!string.IsNullOrEmpty(item.Word))
                            {
                                UpdateWordItemWord(item.WordId, item.Word);
                                savedCount++;
                            }

                            // Definition 업데이트
                            if (!string.IsNullOrEmpty(item.Definition))
                            {
                                UpdateWordItemDefinition(item.WordId, item.Definition);
                                savedCount++;
                            }

                            // Example 업데이트
                            if (!string.IsNullOrEmpty(item.Example))
                            {
                                UpdateWordItemExample(item.WordId, item.Example);
                                savedCount++;
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

