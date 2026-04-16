package innerClass;

import innerClass.Outer.Inner;

public class Outer
{
	private int i = 10;

	public void makeInner()
	{
		Inner in = new Inner();
		in.seeOuter();
	}

	class Inner
	{
		public void seeOuter()
		{
			System.out.println("外部类的域i："+i); // 访问外部类的成员
			System.out.println(this);
			System.out.println(Outer.this);
		}
	}
	public static void main(String[] args)
	{
		new Outer().makeInner();
		
//		Outer outer =new Outer();
		Inner inner = new Outer().new Inner();  //类外要用 Outer.Inner
		inner.seeOuter();
	}
}
