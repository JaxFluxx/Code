package stuCourse;

import java.util.*;

class Student {
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setCourseRecords(List<CourseRecord> courseRecords) {
        this.courseRecords = courseRecords;
    }

    private String id;
    private String name;
    private List<CourseRecord> courseRecords;

    public Student(String id, String name) {
        this.id = id;
        this.name = name;
        this.courseRecords = new ArrayList<CourseRecord>();
    }

    public void addCourseRecord(CourseRecord courseRecord) {
        this.courseRecords.add(courseRecord);
    }

    public List<CourseRecord> getCourseRecords() {
        return Collections.unmodifiableList(courseRecords);
    }
}

class Course {
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getCredits() {
        return credits;
    }

    public void setCredits(int credits) {
        this.credits = credits;
    }

    private String name;
    private int credits;

    public Course(String name, int credits) {
        this.name = name;
        this.credits = credits;
    }
}

class CourseRecord {
    private Course course;

    public Course getCourse() {
        return course;
    }

    public void setCourse(Course course) {
        this.course = course;
    }

    public double getGrade() {
        return grade;
    }

    public void setGrade(double grade) {
        this.grade = grade;
    }

    private double grade;

    public CourseRecord(Course course, double grade) {
        this.course = course;
        this.grade = grade;
    }
}

class CourseManager {
    public Map<String, Student> getStudents() {
        return students;
    }

    public void setStudents(Map<String, Student> students) {
        this.students = students;
    }

    public List<Course> getCourses() {
        return courses;
    }

    public void setCourses(List<Course> courses) {
        this.courses = courses;
    }

    private Map<String, Student> students;
    private List<Course> courses;

    public CourseManager() {
        this.students = new HashMap<>();
        this.courses = new ArrayList<>();
    }

    public void addStudent(Student student) {
        students.put(student.getId(), student);
    }

    public void addCourse(Course course) {
        courses.add(course);
    }

    public void addCourseRecord(String studentId, Course course, double grade) {
        Student student = students.get(studentId);
        if (student != null) {
            student.addCourseRecord(new CourseRecord(course, grade));
        }
    }

    public List<CourseRecord> getStudentCourseRecords(String studentId) {
        Student student = students.get(studentId);
        return student != null ? student.getCourseRecords() : Collections.emptyList();
    }

}

public class stu {
    public static void main(String[] args) {
        // 创建课程
        Course math = new Course("Math", 3);
        Course physics = new Course("Physics", 4);
        Course english = new Course("English", 2);

        // 创建学生
        Student alice = new Student("001", "Alice");
        Student bob = new Student("002", "Bob");
        Student charlie = new Student("003", "Charlie");

        // 创建课程管理器
        CourseManager courseManager = new CourseManager();

        // 加课程
        courseManager.addCourse(math);
        courseManager.addCourse(physics);
        courseManager.addCourse(english);

        // 加学生
        courseManager.addStudent(alice);
        courseManager.addStudent(bob);
        courseManager.addStudent(charlie);

        // 学生添加课程记录
        courseManager.addCourseRecord(alice.getId(), math, 90.5);
        courseManager.addCourseRecord(alice.getId(), physics, 85.0);
        courseManager.addCourseRecord(alice.getId(), english, 88.0);
        courseManager.addCourseRecord(bob.getId(), math, 88.0);
        courseManager.addCourseRecord(bob.getId(), physics, 82.0);
        courseManager.addCourseRecord(charlie.getId(), english, 90.0);

        // 学生的课程记录
        List<CourseRecord> aliceRecords = courseManager.getStudentCourseRecords(alice.getId());
        for (CourseRecord record : aliceRecords) {
            System.out.println(alice.getName() + " took " + record.getCourse().getName() + " and got " + record.getGrade());
        }

        List<CourseRecord> bobRecords = courseManager.getStudentCourseRecords(bob.getId());
        for (CourseRecord record : bobRecords) {
            System.out.println(bob.getName() + " took " + record.getCourse().getName() + " and got " + record.getGrade());
        }

        List<CourseRecord> charlieRecords = courseManager.getStudentCourseRecords(charlie.getId());
        for (CourseRecord record : charlieRecords) {
            System.out.println(charlie.getName() + " took " + record.getCourse().getName() + " and got " + record.getGrade());
        }
    }
}

