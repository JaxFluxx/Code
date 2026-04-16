package equals;

public class Athlete extends Person
{
	private String event;
	public Athlete(String name, String identityNo, String event)
	{
		super(name, identityNo);
		this.event=event;		
	}
	public String getEvent()
	{
		return event;
	}
	
	@Override
	public String toString()
	{
		return super.toString()+"[event=" + event +"]";
	}
}
