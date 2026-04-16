package abstractClasses;


public class ProtectedTest
{
	private String type;
	protected double length;
	public ProtectedTest()	{}
	public ProtectedTest(String t,double l)
	{
		type=t;
		length=l;		
	}
	protected void setType(String t)
	{
		type=t;
	}
	public void show()
	{
		System.out.println("type is " + type);
		System.out.println("length is " + length);
	}
}

class SubProtectedTest extends ProtectedTest
{
	private String color;
	public SubProtectedTest(String c,String t,double l)
	{
		super(t,l);
		color=c;		
	}
	public void setColor(String color)
	{
		this.color=color;
	}
	public void setLength(double len)
	{
		length=len;   //访问父类中的protected域
	}
	public void show()
	{
		super.show();
		System.out.println("color is " + color);
	}
}

class SubTest
{
	public static void main(String[] args)
	{
		ProtectedTest Audi=new ProtectedTest("Audi A4",4.7);
		Audi.setType("Audi A4L");
		Audi.length=4.85;  //访问同一个包中的protected域
		Audi.show();
		SubProtectedTest BMW=new SubProtectedTest("red","BMW320",4.6);
		BMW.setLength(4.75);
		BMW.setType("BMW320L");
		BMW.show();
		
	}
	
}
