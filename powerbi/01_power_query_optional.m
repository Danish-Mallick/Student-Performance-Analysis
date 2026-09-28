// Optional: paste into the Advanced Editor after changing this path.
// Uses the fully prepared CSV written by scripts/analyze.py.
let
    CsvPath = "C:\\REPLACE_WITH_YOUR_PATH\\student-performance-portfolio\\powerbi\\student_performance_powerbi.csv",
    Source = Csv.Document(File.Contents(CsvPath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"Student_ID", Int64.Type}, {"Hours_Studied", Int64.Type},
        {"Attendance", Int64.Type}, {"Exam_Score", Int64.Type},
        {"Sleep_Hours", Int64.Type}, {"Tutoring_Sessions", Int64.Type},
        {"Previous_Scores", Int64.Type}, {"Physical_Activity", Int64.Type},
        {"Study_Range_Order", Int64.Type}, {"Attendance_Band_Order", Int64.Type},
        {"Study_Hours_Range", type text}, {"Attendance_Band", type text},
        {"Tutoring_Group", type text}, {"Score_Quality_Flag", type text},
        {"Teacher_Quality", type text}, {"Extracurricular_Activities", type text},
        {"Parental_Involvement", type text}, {"Access_to_Resources", type text},
        {"Motivation_Level", type text}, {"Internet_Access", type text},
        {"Family_Income", type text}, {"School_Type", type text},
        {"Peer_Influence", type text}, {"Learning_Disabilities", type text},
        {"Parental_Education_Level", type text}, {"Distance_from_Home", type text},
        {"Gender", type text}
    })
in
    Typed
