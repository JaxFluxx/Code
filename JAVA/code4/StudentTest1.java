
/**
 * This is a test to a simple class.
 * @author He Yongqiang
 * @version 1.0 2018-9-28
 *
 */
public class StudentTest1
{
	public static void main(String[] args)
	{
		Student stu1 =new Student("张明", 20, "信息管理","s20170101");
		Student stu2 =new Student("李思成", 21, "信息管理","s20170101");
		Student stu3 =new Student("赵丽丽", 20, "软件工程","s20170203");
		if(stu1.inSameClass(stu2))  
			System.out.println(stu1.getName()+"和"+stu2.getName()+"是同班同学。");
		else
			System.out.println(stu1.getName()+"和"+stu2.getName()+"不是同班同学。");
	}
}

class Student
{
	private String name;
	private int age;
	private String major;
	private String classID;
	public Student() {}
	public Student(String name, int age, String major, String classID)
	{
		this.name = name;
		this.age = age;
		this.major = major;
		this.classID = classID;
	}
	public void say()
	{
		System.out.println("我的名字是"+ name );
		System.out.println("我今年"+ age +"岁");
		System.out.println("我的专业是"+ major);
	}
	public boolean inSameClass(Student stu)
	{
		if(this.classID==stu.classID)
			return true;
		else
			return false;
	}
	public String getName()
	{
		return name;
	}
}
