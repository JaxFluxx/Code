package enums;
/**
 * This program demonstrates enumerated types.
 * @version 1.0 2018-10-24
 * @author He Yongqiang
 */
enum Signal 
{
    GREEN, YELLOW, RED;
}

public class TrafficLight
{
	private Signal color = Signal.RED;

	public void change()
	{
		switch (color)
		{
		case RED:
			color = Signal.GREEN;
			break;
		case YELLOW:
			color = Signal.RED;
			break;
		case GREEN:
			color = Signal.YELLOW;
			break;
		}
	}
	public void getLight()
	{
		System.out.println(color);
	}
	
}

class SignalTest
{
	public static void main(String[] args)
	{
		Signal s1=Signal.YELLOW;
		System.out.println(s1.name());
		System.out.println(s1.toString());
		System.out.println(s1.ordinal());
		Signal s2=Signal.YELLOW;
		System.out.println(s1==s2);
			
		
		Signal[] light=Signal.values();
		for(Signal s:light)
			System.out.println(s);
	
		TrafficLight trafficLight=new TrafficLight();
		trafficLight.getLight();
		trafficLight.change();
		trafficLight.getLight();
		
	}
}
