namespace WpfAppCvoca.Services
{
    /// <summary>
    /// SQL 쿼리문을 관리하는 정적 클래스
    /// </summary>
    public static class SQLiteQueries
    {
        // ========== Words 관련 쿼리 ==========
        
        public const string LoadAllWords = @"
            SELECT word_id, day_no, word_no, word
            FROM words
            ORDER BY day_no, word_no;
        ";

        public const string LoadWordsByDay = @"
            SELECT word_id, day_no, word_no, word
            FROM words
            WHERE day_no = @day_no
            ORDER BY word_no;
        ";

        public const string UpdateWord = @"
            UPDATE words
            SET word = @word
            WHERE word_id = @word_id;
        ";

        // ========== WordItems 관련 쿼리 (LayoutMode별) ==========

        public const string LoadWordOnly = @"
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

        public const string LoadDefinitionOnly = @"
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

        public const string LoadExampleOnly = @"
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

        public const string LoadWordDefinition = @"
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

        public const string LoadDefinitionExample = @"
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

        public const string LoadWordDefinitionExample = @"
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

        // ========== Update 관련 쿼리 ==========

        public const string UpdateWordItemDefinition = @"
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

        public const string UpdateWordItemExample = @"
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

        public const string UpdateWordItemDefinitionByDefinitionId = @"
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

        public const string UpdateWordItemExampleByDefinitionId = @"
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
    }
}

