package methodsConflict;

public class MainOfPerson
{

	public static void main(String[] args)
	{
		Student s1=new Student("John Black","33005566","software engineering");
		System.out.println(s1.getName());
		
		
		Worker w1=new Worker("赵一鸣",30);
		System.out.println(w1.getName());

	}

}
