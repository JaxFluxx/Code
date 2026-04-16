package equals;

public class MainOfPerson
{

	public static void main(String[] args)
	{
		Person[] person =new Person[3];
		person[0]=new Student("张伟","1101089999","软件工程");
		person[1]=new Athlete("张伟","1101089999","篮球");
		if(person[0].equals(person[1]))
			System.out.println("person[0]和person[1]是同一个人。");
		
		Student s1=new Student("王芳","1101006666","机械工程");
		Athlete a1=new Athlete("王芳","1101006666","游泳");
		System.out.println(s1);
		System.out.println(a1);
		if(a1.equals(s1))
			System.out.println("a1和s1是同一个人。");

	}

}
