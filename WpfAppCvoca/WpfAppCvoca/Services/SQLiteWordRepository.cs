using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
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
                using (var conn = new SqliteConnection($"Data Source={dbPath}"))
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
                using (var conn = new SqliteConnection($"Data Source={dbPath}"))
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
                using (var conn = new SqliteConnection($"Data Source={dbPath}"))
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
                using (var conn = new SqliteConnection($"Data Source={dbPath}"))
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
    }
}

