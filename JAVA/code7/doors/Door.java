package doors;
/**
 * This program displays a test for the interface operations .
 * @version 1.1 2021-11-25
 * @author He Yongqiang
 */
public abstract class Door
{
	private int length;
	private int width;
	private String color;
	public Door() {}
	public Door(int length, int width, String color)
	{
		this.length=length;
		this.width=width;
		this.color=color;
	}
	public abstract void open()throws InterruptedException;
    public abstract void close();
}
