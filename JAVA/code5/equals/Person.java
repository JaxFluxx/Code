package equals;

import java.util.Objects;
/**
 * This class displays a test for the equals, hashCode and toString methods.
 * The equals and hashCode here are  final methods.
 * @version 1.0 2018-11-28
 * @author He Yongqiang
 */
public class Person
{
	private String name;
	private String identityNo;
	
	public Person() {}
	public Person(String name, String identityNo)
	{
		this.name=name;
		this.identityNo=identityNo;		
	}
	
	public String getName()
	{
		return name;
	}
	public String getIdentityNo()
	{
		return identityNo;
	}
	//overrides java.lang.Object.equals
	@Override  
	public final boolean equals(Object otherObject)
	{
		if(this==otherObject)
			return true;
		if(otherObject==null)
			return false;
		if(!(otherObject instanceof Person))
			return false;
		Person other=(Person)otherObject;
		return Objects.equals(this.name, other.name) && Objects.equals(this.identityNo, other.identityNo);
	}
	//overrides java.lang.Object.hashCode
	@Override
	public final int hashCode()
	{
		return Objects.hash(name,identityNo);
	}
	//overrides java.lang.Object.toString
	@Override
	public String toString()
	{
		return getClass().getName() + "[name="+ name +"identityNo="+ identityNo +"]";
	}
	
}
