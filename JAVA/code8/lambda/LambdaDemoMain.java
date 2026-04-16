package lambda;
/**
 * 
 * @author hyq
 *
 */
public class LambdaDemoMain
{
	public static void main(String[] args)
	{
		//调用实例方法
		LambdaDemo ld = new LambdaDemo(10,20,"Hello");
		System.out.println(ld.calInt((a,b)->a+b));
		
		//lambda表达式表示一个接口子类的对象，可以赋值给接口变量
		Operation oper=(a,b)->a*a+b*b;
		System.out.println(ld.calInt(oper));
		
		ld.ShowMessage(m->System.out.println("The message in class is: "+m));
		
		//调用类方法
		int ia=1024;
		int ib=512;
		int ic=LambdaDemo.staticCalInt(ia, ib, (x,y)->x+y);
		System.out.println(ic);
		
		String message="Welcome, java.";
		LambdaDemo.staticMessage(message, m->System.out.println("The message out of class is: "+m));
		
	}
}
