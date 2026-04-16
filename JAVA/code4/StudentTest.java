
/**
 * This is a test to a simple class.
 * @author He Yongqiang
 * @version 1.0 2018-9-28
 *
 */
public class StudentTest
{
	public static void main(String[] args)
	{
		Student 李华 = new Student();
		李华.name = "李华";
		李华.age = 21;
		李华.major = "软件工程";
		李华.say();	
		Student stu1 =new Student("张明", 20, "信息管理");
		stu1.say();
	}
}

class Student
{
	public String name;
	public int age;
	public String major;
	public Student() {}
	public Student(String name, int age, String major)
	{
		this.name = name;
		this.age = age;
		this.major = major;
	}
	public void say()
	{
		System.out.println("我的名字是"+ name );
		System.out.println("我今年"+ age +"岁");
		System.out.println("我的专业是"+ major);
	}
}
