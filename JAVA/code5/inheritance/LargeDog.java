package inheritance;
/**
 * This is a class which extended from Dog class.
 * 
 * @version 1.0, 2018-10-19.
 * @author He Yongqiang.
 *
 */
public class LargeDog extends Dog
{
	private double weight;
	
	public static void info()
	{
		System.out.println("LargeDog类描述巨型犬。");
	}

	public LargeDog(int weight)
	{
		this.weight=weight;
	}
	public LargeDog(String name, String color, double age,double weight)
	{
		super(name,color,age);
		this.weight=weight;
	}
	
	@Override
	public void run()
	{
		System.out.println("我可以跑的飞快！");
	}
	@Override
	public void show()
	{
		super.show();
		System.out.println("weight:"+weight);
		
	}
	public double getWight()
	{
		return weight;
	}
}
