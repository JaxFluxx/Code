package methodsConflict;

public class Student extends Person implements Named
{
	private String major;
	public Student(String name, String identityNo, String major)
	{
		super(name, identityNo);
		this.major=major;		
	}
	public String getMajor()
	{
		return major;
	}
	
	@Override
	public String toString()
	{
		return super.toString()+"[major=" +major +"]";
	}
}
