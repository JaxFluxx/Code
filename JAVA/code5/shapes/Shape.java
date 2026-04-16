package shapes;

/**
 * @version 1.1 2021-11-24
 * @author He Yongqiang
 */
public abstract class Shape
{
	private String color;

	public Shape(){}
	public Shape(String color)
	{
		this.color = color;
	}
	public void setColor(String color)
	{
		this.color = color;
	}
	public String getColor()
	{
		return this.color;
	}
	
	public abstract double getPerimeter();  //返回图形的周长
	public abstract double getArea();       //返回图形的面积
	public abstract void move(int x,int y);            //移动图形:在横轴和纵轴分别移动x，y
	
}
