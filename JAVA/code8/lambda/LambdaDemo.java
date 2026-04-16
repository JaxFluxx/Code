package lambda;
/**
 * 
 * @author He, Yongqiang
 *
 */
public class LambdaDemo
{
	private String aString;
	private int x;
	private int y;
	

	public LambdaDemo(int x, int y,String aString)
	{
		this.aString=aString;
		this.x=x;
		this.y=y;
	}
	//实例方法，方法的参数是一个接口对象，计算数是实例中的域
	public int calInt(Operation o)
	{
		return o.operate(x, y);
	}
	public void ShowMessage(MessageInterface m)
	{
		m.sayMessage(aString);
	}
	//类方法的前两个参数传入操作数，第三个参数传入算法代码块
	public static int staticCalInt(int x, int y,Operation o)
	{
		return o.operate(x, y);
	}
	
	public static void staticMessage(String s, MessageInterface m)
	{
		m.sayMessage(s);
	}
	
}

///////////////////////////////////////////////////////////////
interface Operation
{
	int operate(int x, int y);
}

interface MessageInterface
{
	void sayMessage(String message);
}