package inheritance;

import java.awt.Point;

public class PointTest
{

	public static void main(String[] args)
	{
		Point p1=new Point(10,20);
		Point p2=new Point(-8,-25);
		System.out.println(p1);
		p2.move(10, 20);
		System.out.println(p2);
		System.out.println(p1.equals(p2));
	}

}
