/**
 * 
 * @author He Yongqiang
 * @version 1.1, 2021-11-04
 */

public class Point
{

	private double x;
	private double y;
	private double rho;
	private double theta;
	
	public Point()
	{
		x=0.0;
		y=0.0;
		rho=0.0;
		theta=0.0;
	}
	public Point(double v,double w,char flag)     //C表示直角坐标，P表示极坐标
	{
		if (flag=='c'||flag=='C')
		{
			this.x=v;
			this.y=w;
			cartesianToPolar();
		}
		else if(flag=='p'||flag=='P')
		{
			this.rho=v;
			this.theta=w;
			polarToCartesian();
		}
		else
			System.out.print("You should set the flag as \"C\" or\"P\". \nYou got an origin point just now.\n");
		
	}
	private void cartesianToPolar()
	{
		rho=Math.sqrt(x*x+y*y);
		theta=Math.atan2(y, x);
	}
	private void polarToCartesian()
	{
		x=rho*Math.cos(theta);
		y=rho*Math.sin(theta);
	}
	public void showPointInCartesian()
	{
		System.out.println("x="+ x +", y=" +y);
	}
	public void showPointInPolar()
	{
		System.out.println("rho="+ rho +", theta=" +theta);
	}
	
	/////////////////////////////////////////////////
	public static void main(String[] args)
	{
		Point myPoint=new Point(14,0.785,'p');
		myPoint.showPointInCartesian();
		myPoint.showPointInPolar();
	}
	
}
