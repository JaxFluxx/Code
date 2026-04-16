package methodsConflict;

public class Worker implements  Named, OtherNamed
{
	private String name;
	private int age;
	public Worker(String name, int age)
	{
		this.name=name;
		this.age=age;
	}
	public String getName()
	{
//		return OtherNamed.super.getName();
		return name;
	}
}
