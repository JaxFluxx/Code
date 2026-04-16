package javatest;


/**
 * 该程序演示了static成员和非static成员之间的访问关系.
 * 
 * @version 1.0 2021-11-09
 * @author He Yongqiang
 */
public class StaticMember {
	
	private int x;	
	private static int z;
	
	public static void main(String[] args) {
		//main是static方法，可以访问本类的static成员：
		System.out.println("z is: "+ z);
		//下面的访问是错误的：
	    //System.out.println("x is: "+ x);
	    //必须建立对象，通过对象访问非static成员：
		StaticMember m1=new StaticMember();
		System.out.println("m1.x= " + m1.x);
				
	}
	//供类外访问static成员的共有接口，也必须是static方法：
	public int getx()
	{
		return x;
	}
	public static int getz()
	{
		return z;
	}
}
    

//以下是在类外进行访问StaticMember类的成员：
class StaticMemberTest{
	public static void main(String[] args) {
		//由于z是私有成员，必须通过其所在类中的公有方法访问：
		System.out.println(StaticMember.getz());
		//访问非static成员必须通过对象进行，由于x是私有的，也要通过其所在类中的公有方法访问：
		StaticMember m2=new StaticMember();
		System.out.println(m2.getx());
		
	}	
}
