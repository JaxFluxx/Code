package doors;

import java.awt.Toolkit;
/**
 * This program displays a test for the interface operations .
 * @version 1.1 2021-11-25
 * @author He Yongqiang
 */
public class AlarmDoor extends Door implements Alarm
{
	private int grade;
	public AlarmDoor() {}
	public AlarmDoor(int length, int width, String color, int grade)
	{
		super(length,  width,  color);
		this.grade =grade;
	}
	@Override
	public void open() throws InterruptedException
	{
		System.out.println("The door is opening.");
		addInfo();
		alarm();
		
	}
	@Override
	public void close()
	{
		System.out.println("The door is closed.");
	}
	@Override
	public void alarm() throws InterruptedException 
	{
		for (int i = 0;i<10;i++) {
			  Toolkit.getDefaultToolkit().beep();
			  Thread.sleep(1000);
			}
	}
}
