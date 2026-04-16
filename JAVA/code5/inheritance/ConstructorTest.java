package inheritance;

public class ConstructorTest
{
	public static void main(String[] args)
	{
		Sub aSub=new Sub();
	}
}

class Super 
{
	private String s;
	public Super(String s) 
	{
		this.s=s;
	}
	public Super()
	{
		
	}
}

class Sub extends Super
{
	private int x=100;
	public Sub()
	{
		System.out.println("Sub");
	}
		
}
