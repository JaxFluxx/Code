/**
 * 这个程序演示了this的用法。
 * @author hyq
 * @version 1.0 2018-9-29
 */
public class AirPlane
{
	private String airPlaneID;
	public AirPlane(String id)
	{
		airPlaneID = id;
	}
	public void taxiing()
	{
		System.out.println(airPlaneID + " is taxiing now.");
	}
	public void takeOff()
	{
		this.taxiing();
		System.out.println(airPlaneID + " is taking off now.");
	}
}

class AirPlaneTest
{
	public static void main(String[] args)
	{
		AirPlane ap1 = new AirPlane("CA1400");
		ap1.taxiing();
		ap1.takeOff();
	}
}